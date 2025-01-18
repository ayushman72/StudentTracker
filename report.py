import json
import requests

from typer import Typer

from trackers import MassTracker

def json_loader(path: str) -> dict:
    if path.startswith('https://'):
        try:
            resp = requests.get(path)
            resp.raise_for_status()  
            return json.loads(resp.content)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch data from URL: {path}. Error: {e}")
    elif path.lower().endswith('.json'):
        try:
            with open(path) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to load JSON file: {path}. Error: {e}")
    raise ValueError("Only URLs starting with https:// or files ending with .json are supported.")


app = Typer()

@app.command()
def analyze(history: str, quiz_to_check: str | None = None, output_path: str = 'out.png') -> None:
    try:
        history_dict = json_loader(history)
    except ValueError as e:
        print(f"Error loading history: {e}")
        return

    trackers = MassTracker(history_dict)

    swot = trackers.SWOTAnalysis()
    
    def line_printer(key: str):
        for s in swot.get(key, []):
            print("-", s)

    print("Strengths:\n")
    line_printer('S')
    print("\nWeaknesses:\n")
    line_printer('W')
    print("\nOpportunities:\n")
    line_printer('O')
    print("\nThreats:\n")
    line_printer('T')
    print("\n\nSuggestions:\n")
    line_printer('suggestions')

    trackers.SWOTImage(output_path)

    if quiz_to_check:
        try:
            quiz = json_loader(quiz_to_check)
            trackers.compare_from_past(quiz)
        except ValueError as e:
            print(f"Error loading quiz: {e}")

        
if __name__ == "__main__":
    app()