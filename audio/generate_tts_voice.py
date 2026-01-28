import argparse
import torch
from TTS.api import TTS

def generate_speech1(text, output_path, model_name, speaker_wav=None):
    # Get device
    device = "mps" if torch.mps.is_available() else "cpu"
    print(f"Using device: {device}")

    # Initialize TTS model
    print(f"Loading model: {model_name}...")
    tts = TTS(model_name).to(device)

    # Run TTS
    print("Synthesizing...")
    if speaker_wav:
        # For voice cloning (XTTS)
        tts.tts_to_file(text=text, speaker_wav=speaker_wav, language="en", file_path=output_path)
    else:
        # For standard models
        tts.tts_to_file(text=text, file_path=output_path)
    
    print(f"Audio saved to: {output_path}")


def generate_speech(text, output_path, model_name, speaker_name):
    """
    Generates a speech WAV file using Coqui TTS with optional speaker selection.
    """
    # Determine device (cuda or cpu)
    device = "mps" if torch.mps.is_available() else "cpu"

    print(f"Loading model: {model_name} on {device}...")
    try:
        # Initialize TTS model
        tts = TTS(model_name=model_name).to(device)
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please check available models using the CLI command: tts --list_models")
        return


    # List speakers if a speaker index might be needed and the model supports it
    # print(f"Available speakers for this model: {tts.speakers}")
    # tts_models/en/vctk/vits
    # Available speakers for this model: ['ED\n', 'p225', 'p226', 'p227', 'p228', 'p229', 
    # 'p230', 'p231', 'p232', 'p233', 'p234', 'p236', 'p237', 'p238', 'p239', 'p240', 
    # 'p241', 'p243', 'p244', 'p245', 'p246', 'p247', 'p248', 'p249', 'p250', 'p251', 
    # 'p252', 'p253', 'p254', 'p255', 'p256', 'p257', 'p258', 'p259', 'p260', 'p261', 
    # 'p262', 'p263', 'p264', 'p265', 'p266', 'p267', 'p268', 'p269', 'p270', 'p271', 
    # 'p272', 'p273', 'p274', 'p275', 'p276', 'p277', 'p278', 'p279', 'p280', 'p281', 
    # 'p282', 'p283', 'p284', 'p285', 'p286', 'p287', 'p288', 'p292', 'p293', 'p294', 
    # 'p295', 'p297', 'p298', 'p299', 'p300', 'p301', 'p302', 'p303', 'p304', 'p305', 
    # 'p306', 'p307', 'p308', 'p310', 'p311', 'p312', 'p313', 'p314', 'p316', 'p317', 
    # 'p318', 'p323', 'p326', 'p329', 'p330', 'p333', 'p334', 'p335', 'p336', 'p339', 
    # 'p340', 'p341', 'p343', 'p345', 'p347', 'p351', 'p360', 'p361', 'p362', 'p363', 
    # 'p364', 'p374', 'p376']
    # tts_models/multilingual/multi-dataset/xtts_v2
    # 'Claribel Dervla', 'Daisy Studious', 'Gracie Wise', 'Tammie Ema', 'Alison Dietlinde', 
    # 'Ana Florence', 'Annmarie Nele', 'Asya Anara', 'Brenda Stern', 'Gitta Nikolina', 
    # 'Henriette Usha', 'Sofia Hellen', 'Tammy Grit', 'Tanja Adelina', 'Vjollca Johnnie', 
    # 'Andrew Chipper', 'Badr Odhiambo', 'Dionisio Schuyler', 'Royston Min', 'Viktor Eka', 
    # 'Abrahan Mack', 'Adde Michal', 'Baldur Sanjin', 'Craig Gutsy', 'Damien Black', 
    # 'Gilberto Mathias', 'Ilkin Urbano', 'Kazuhiko Atallah', 'Ludvig Milivoj', 
    # 'Suad Qasim', 'Torcull Diarmuid', 'Viktor Menelaos', 'Zacharie Aimilios', 
    # 'Nova Hogarth', 'Maja Ruoho', 'Uta Obando', 'Lidiya Szekeres', 
    # 'Chandra MacFarland', 'Szofi Granger', 'Camilla Holmström', 'Lilya Stainthorpe', 
    # 'Zofija Kendrick', 'Narelle Moon', 'Barbora MacLean', 'Alexandra Hisakawa', 
    # 'Alma María', 'Rosemary Okafor', 'Ige Behringer', 'Filip Traverse', 'Damjan Chapman', 
    # 'Wulf Carlevaro', 'Aaron Dreschner', 'Kumar Dahl', 'Eugenio Mataracı', 'Ferran Simen', 
    # 'Xavier Hayasaka', 'Luis Moray', 'Marcos Rudaski'
    # Use speaker name from index (Coqui API uses speaker names/IDs, not raw indices in the function call)
    # speaker_name = tts.speakers[speaker_idx]
    print(f"Using speaker: {speaker_name}")

    # List speakers if a speaker index might be needed and the model supports it
    #if speaker_idx is not None and len(tts.speakers) > 1:
    #    print(f"Available speakers for this model: {tts.speakers}")
    #    if speaker_idx < 0 or speaker_idx >= len(tts.speakers):
    #        print(f"Error: Speaker index {speaker_idx} is out of range.")
    #        return
    #    # Use speaker name from index (Coqui API uses speaker names/IDs, not raw indices in the function call)
    #    speaker_name = tts.speakers[speaker_idx]
    #    print(f"Using speaker: {speaker_name}")
    #elif speaker_idx is not None and len(tts.speakers) <= 1:
    #    print("Warning: Model is single-speaker or speaker index not applicable. Ignoring speaker_idx.")
    #    speaker_name = None
    #else:
    #    speaker_name = None

    print(f"Synthesizing speech for text: '{text}'...")
    try:
        # Generate speech
        tts.tts_to_file(
            text=text,
            speaker=speaker_name,
            language="en",
            file_path=output_path
        )
        print(f"Successfully generated speech and saved to {output_path}")
    except Exception as e:
        print(f"Error during speech synthesis: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Coqui TTS Script")
    parser.add_argument("-t", "--text", type=str, required=True, help="Text to convert to speech")
    parser.add_argument("-o", "--output", type=str, default="out.wav", help="Path to save output .wav file")
    parser.add_argument("-m", "--model", type=str, default="tts_models/multilingual/multi-dataset/xtts_v2", help="Coqui TTS model name")
    parser.add_argument("--speaker_wav", type=str, help="Path to reference audio for voice cloning (optional)")
    parser.add_argument("-n", "--speaker_name", type=str, help="Speaker name")

    args = parser.parse_args()

    # The Coqui API often uses speaker names/IDs. The script above handles mapping index to name if needed.
    # The user can check available speakers via the Coqui CLI: `tts --model_name "<model_name>" --list_speaker_idxs`
    generate_speech(args.text, args.output, args.model, args.speaker_name)

