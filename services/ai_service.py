import os
import openai
import asyncio
import random
import bisect
from dotenv import load_dotenv

from repositories.discord_bot_repository import DiscordBotRepository
from services.discord_bot import MyBot

load_dotenv()

VENICE_API_KEY = os.getenv("VENICE_API_KEY")
BASE_URL = "https://api.venice.ai/api/v1"
MODEL_ID = "venice-uncensored"

class AIMessageService:
    def __init__(self, repo: DiscordBotRepository):
        self.repo = repo
        if not VENICE_API_KEY:
            raise ValueError("VENICE_API_KEY not set")

        self.client = openai.OpenAI(
            api_key=VENICE_API_KEY,
            base_url=BASE_URL,
            timeout=30.0
        )

    async def generate_message(self, selected_bot: MyBot, conversation_context: str):
        # 1. Update irritation
        irritation_string, irritation_real = await self.update_and_get_irritation_label(selected_bot, conversation_context)
        print("irritation is: " + str(irritation_real))

        # 2. Determine if the bot spoke last
        def get_last_speaker(conversation_context: str) -> str:
            lines = [line for line in conversation_context.splitlines() if line.strip()]
            if not lines:
                return None
            last_line = lines[-1]
            if ":" in last_line:
                return last_line.split(":", 1)[0].strip()
            return None

        last_speaker = get_last_speaker(conversation_context)
        last_speaker_rule = (last_speaker == selected_bot.name)

        # 2. Generate a concise summary of the conversation
        def _summarize_context():
            summary_prompt = f"""

            You are {selected_bot.name} in this conversation.
            Summarize the conversation that was had so far in up to 4-8 sentences.

            STRICT RULES:
            - 1. ONLY summarize information that is explicitly stated in the conversation.
            - 2. Do NOT interpret tone, sentiment, or intention. Just report the facts as they appear.
            - 3. DO NOT include instructions for the bot, personality cues
            - 4. DO NOT generalize or add context that is not directly mentioned.
            {"- 5. Note that you spoke last and list the key points you mentioned. Focus on yourself, Clearly note that YOU SPOKE LAST, so you should build upon your last point and lay out the last point you were making." if last_speaker_rule else "- 5. Focus on the latest message in the conversation. Make it clear what is being discussed and highlight that as the main point, so the next reply will naturally continue the conversation."}

            Additionally:
            - PRIORITIZE developing the current topic. Only suggest a pivot to a new topic if the same topic has been repeated multiple times or cannot be expanded naturally or the conversation is getting boring.
            - If suggesting a pivot, clearly note which topic to stop talking about and what new topic or angle to move to.
            - Include cues for natural continuation, such as asking a question, adding personal experience, or expanding on details.
            - If a new topic is introduced (e.g. exes, drama, personal history, whatever), explicitly state what details are expected next (who, what happened, when, or why), so the next reply must expand instead of reintroducing the topic.

            THE NUMBER ONE PRIORITY IS FOR THIS TO BE FUNNY AS FUCK AND DRAMA FILLED.

            Conversation history so far in the Discord server (do not repeat verbatim):
            {conversation_context}
            """
                
            summary_response = self.client.chat.completions.create(
                model=MODEL_ID,
                messages=[{"role": "user", "content": summary_prompt}],
                temperature=0.3
            )
            return summary_response.choices[0].message.content.strip()

        summary = await asyncio.to_thread(_summarize_context)
        print("Conversation summary:\n" + summary)

        # 3. Build system prompt with summary
        system_prompt = f"""        
        1. You are a participant in a Discord server conversation. Always act in-character for the given bot. 
        2. Speak ONLY in first person, as live dialogue - Speak in first person as yourself, using "I" and "me," never your name.
        3. Never acknowledge that you are an AI or reference any outside context. 
        4. Follow the bot's personality traits strictly. 
        5. Focus on short, reactive, natural messages, like in a real Discord chat.
        6. Do not invent conversation history; only respond based on provided context, do not loop in your replies.
        7. Be dynamic, create drama and add to the flow of the conversation, NEVER make it stale, do not repeat yourself. 
        8. This is a DISCORD conversation, so shorter messages are preferred. 
        9. Do not repeat yourself.
        """.strip()

        # Optional random rarePrompt injection
        extra_guidance = "\n\n" + random.choices(
        [
        # Develop the current topic with humor or drama
        "Build on the latest message, adding humor, drama, or witty commentary, keeping the conversation lively and in-character.",

        # React creatively while staying on topic
        "React to what was just said, add your perspective, personal experience, or bold opinion, ensuring the discussion develops naturally from the latest point.",

        # Subtle expansion without unnecessary topic shifts
        "Expand on the current discussion with interesting details, anecdotes, or playful teasing, without randomly changing the subject.",

        # Pivot only if needed
        "If the topic has been repeated or is stale, subtly introduce a fresh angle or related story, but ensure it feels like a natural continuation of the conversation.",

        # Encourage engagement while staying reactive
        "Engage with the latest message, challenge opinions, or escalate drama in a short, natural, and entertaining way, keeping the conversation flowing."
        ],
        weights=[0.3, 0.25, 0.2, 0.15, 0.1],
        k=1
        )[0]

        # 4. Call Venice AI with the summary as context
        def _call_api():
            print("Venice request started")
            response = self.client.chat.completions.create(
                model=MODEL_ID,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{selected_bot.basePrompt}, your current irritation is: {irritation_string}, optional guidance for what to do next: {extra_guidance}. The current narration of the conversation so far, this is IMPORTANT: {summary}. This is a DISCORD conversation, keep messages 2-4 sentence long. Using the narration as context, write a new Discord message in your own words, STAY TRUE TO YOUR CHARACTER. Do NOT reuse exact phrases or sentences from narration. Keep it short, natural, your reply should naturally continue the conversation and focus on the latest point in the narration or any points that are addressed at you, remember YOU ARE {selected_bot.name} so ACT LIKE IT."}
                ],
                extra_body={
                    "venice_parameters": {
                        "include_venice_system_prompt": False
                    }
                },
                temperature=0.85
            )
            print("Venice response received")
            return response.choices[0].message.content
        return await asyncio.to_thread(_call_api)

    def get_last_speaker(conversation_context: str) -> str:
        # Get all non-empty lines
        lines = [line for line in conversation_context.splitlines() if line.strip()]
        if not lines:
            return None
        # Take the last line
        last_line = lines[-1]
        if ":" in last_line:
            return last_line.split(":", 1)[0].strip()
        return None

    
    async def update_and_get_irritation_label(
        self,
        selected_bot: MyBot,
        conversation_context: str
    ) -> tuple[str, float]:

        # 1. Read current irritation (0.0 → 1.2)
        current_irritation = await self.repo.get_irritation(selected_bot.name)
        print("CURRENT IRRITATION into DB is: " + str(current_irritation))

        # 2. Compute delta
        delta = random.randint(-5, 15) / 100.0
        mentioned_flag = False
        bot_name_lower = selected_bot.name.lower()

        for line in conversation_context.splitlines():
            if ":" not in line:
                continue

            speaker, message = line.split(":", 1)
            speaker = speaker.strip().lower()
            message = message.strip().lower()

            # Ignore messages from the bot itself
            if speaker == bot_name_lower:
                continue

            # Mention spike (once)
            if not mentioned_flag and bot_name_lower in message:
                delta += 0.10
                mentioned_flag = True

        # 3. Apply delta (NO premature clamp)
        raw_irritation = current_irritation + delta

        # 4. Meltdown reset at 1.2
        if raw_irritation >= 1.2:
            new_irritation = 0.0
        else:
            new_irritation = max(0.0, min(raw_irritation, 1.2))

        print("NEW irritation to insert into DB is: " + str(new_irritation))

        # 5. Persist
        await self.repo.update_irritation(
            bot_name=selected_bot.name,
            irritation=new_irritation
        )

        # 6. Labeling (cap ONLY for label logic)
        value_for_label = min(new_irritation, 1.0)

        irritation_label = ["LOW", "MEDIUM", "HIGH", "CRITICAL"][
            bisect.bisect([0.2, 0.5, 0.7], value_for_label)
        ]

        return irritation_label, new_irritation
