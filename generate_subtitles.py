import os

def generate_subtitles(script, output_path="output/subtitles.srt"):
    os.makedirs("output", exist_ok=True)
    lines = script.strip().split(". ")
    with open(output_path, "w") as f:
        for i, line in enumerate(lines):
            start_time = i * 4
            end_time = (i + 1) * 4
            f.write(f"{i+1}\n")
            f.write(f"00:00:{start_time:02d},000 --> 00:00:{end_time:02d},000\n")
            f.write(line.strip() + "\n\n")
    return output_path
