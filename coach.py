import os
import json
import csv
import openai

class SleepCoach:
    """
    Sleep coaching agent that generates responses using user's sleep data and an LLM.
    """
    def __init__(self, diary_csv_path, metrics_json_path, dialogues_json_path=None):
        # Load sleep diary entries (CSV)
        self.diary_entries = self._load_diary(diary_csv_path)
        # Load sleep metrics (JSON)
        self.metrics = self._load_metrics(metrics_json_path)
        # Load example coaching dialogues (optional, JSON)
        self.example_dialogues = self._load_dialogues(dialogues_json_path) if dialogues_json_path else []
        # Define a base system prompt for the coach's persona
        self.coach_instructions = (
            "You are a virtual sleep coach assistant. "
            "Be empathetic, friendly, and provide helpful advice about sleep. "
            "You have access to the user's sleep diary and wearable data."
        )
        # Ensure OpenAI API key is set (for generating responses)
        if not openai.api_key:
            print("Warning: OpenAI API key not set. Responses will not be generated without it.")

    def _load_diary(self, path):
        entries = []
        if path and os.path.exists(path):
            try:
                with open(path, 'r', newline='') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        entries.append({
                            "date": row.get("Date", ""), 
                            "entry": row.get("Entry", "")
                        })
            except Exception as e:
                print(f"Error loading diary CSV: {e}")
        else:
            print("Sleep diary file not found or not provided.")
        return entries

    def _load_metrics(self, path):
        data = []
        if path and os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Error loading metrics JSON: {e}")
        else:
            print("Sleep metrics file not found or not provided.")
        return data

    def _load_dialogues(self, path):
        examples = []
        if path and os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    examples = json.load(f)
            except Exception as e:
                print(f"Error loading dialogues JSON: {e}")
        return examples

    def _get_latest_data_context(self):
        """
        Compile the latest diary entry and metrics into a context string for the prompt.
        """
        latest_diary = self.diary_entries[-1] if self.diary_entries else None
        latest_metrics = self.metrics[-1] if self.metrics else None
        context_lines = []
        if latest_diary:
            context_lines.append(f"Last Diary ({latest_diary['date']}): {latest_diary['entry']}")
        if latest_metrics:
            date = latest_metrics.get("date")
            score = latest_metrics.get("sleep_score")
            hours = latest_metrics.get("hours") or latest_metrics.get("sleep_duration")
            context_lines.append(f"Wearable Data ({date}): Sleep Score {score}, Hours Slept {hours}")
        return "\n".join(context_lines)

    def generate_coach_response(self, user_text):
        """
        Generate a coaching response to the user's text input using the LLM (OpenAI API).
        """
        # Build the message list for OpenAI ChatCompletion
        system_msg = {"role": "system", "content": self.coach_instructions}
        messages = [system_msg]
        # Include latest diary/metrics context as additional system info
        context_info = self._get_latest_data_context()
        if context_info:
            messages.append({"role": "system", "content": f"Context:\n{context_info}"})
        # User message
        messages.append({"role": "user", "content": user_text})
        # Call OpenAI to get the assistant's response
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=400,
                temperature=0.7
            )
            answer = response['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"Error generating coach response: {e}")
            # Fallback: if LLM fails, use an example dialogue if it matches or a default line
            answer = "I'm here to help with your sleep."
            for ex in self.example_dialogues:
                if ex.get("user") and ex["user"].lower() in user_text.lower():
                    answer = ex.get("coach", answer)
                    break
        return answer
