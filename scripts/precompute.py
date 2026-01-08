"""
precompute embeddings for all audio files in a directory.
usage: python scripts/precompute.py "A:\Resume K8 Project\recommendation corpus"
"""

import sys
import pickle
import re
from pathlib import Path
import torch
import librosa
from transformers import ClapModel, ClapProcessor

def clean_song_name(filename: str) -> str:
    """
    turn '001-2285379-Square a Saw-Echoes.mp3' 
    into 'Square a Saw - Echoes'
    """
    # remove extension
    name = Path(filename).stem
    
    # jamendo format: XXX-XXXXXXX-Artist-Title
    # split by dash and take last two parts (artist and title)
    parts = name.split('-')
    if len(parts) >= 4:
        artist = parts[2]
        title = '-'.join(parts[3:])  # in case title has dashes
        return f"{artist} - {title}"
    
    # fallback: just return the filename without numbers at start
    cleaned = re.sub(r'^\d+[-_\s]*', '', name)
    return cleaned if cleaned else name

def main(audio_dir: str):
    audio_path = Path(audio_dir)
    
    # find all audio files
    extensions = ['*.mp3', '*.wav', '*.flac', '*.ogg']
    audio_files = []
    for ext in extensions:
        audio_files.extend(audio_path.glob(ext))
    
    if not audio_files:
        print(f"no audio files found in {audio_dir}")
        sys.exit(1)
    
    print(f"found {len(audio_files)} audio files")
    print("loading clap model...")
    
    processor = ClapProcessor.from_pretrained("laion/clap-htsat-unfused")
    model = ClapModel.from_pretrained("laion/clap-htsat-unfused")
    model.eval()
    
    print("model loaded, processing audio files...\n")
    
    names = []
    embeddings = []
    failed = []
    
    for i, audio_file in enumerate(audio_files):
        print(f"[{i+1}/{len(audio_files)}] {audio_file.name[:50]}...", end=" ")
        
        try:
            # load audio at 48khz (what clap expects)
            waveform, sr = librosa.load(audio_file, sr=48000)
            
            # clap works best with ~10s chunks, take from middle
            max_samples = 10 * 48000
            if len(waveform) > max_samples:
                start = (len(waveform) - max_samples) // 2
                waveform = waveform[start:start + max_samples]
            
            inputs = processor(audios=waveform, sampling_rate=48000, return_tensors="pt")
            
            with torch.no_grad():
                audio_embed = model.get_audio_features(**inputs)
            
            clean_name = clean_song_name(audio_file.name)
            names.append(clean_name)
            embeddings.append(audio_embed.numpy().flatten())
            print("ok")
            
        except Exception as e:
            print(f"FAILED: {e}")
            failed.append(audio_file.name)
            continue
    
    if not embeddings:
        print("no embeddings generated!")
        sys.exit(1)
    
    import numpy as np
    embeddings_array = np.stack(embeddings)
    
    output_path = Path("data/embeddings.pkl")
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, "wb") as f:
        pickle.dump({
            "names": names, 
            "embeddings": embeddings_array
        }, f)
    
    print(f"\n{'='*50}")
    print(f"saved {len(names)} embeddings to {output_path}")
    print(f"embedding shape: {embeddings_array.shape}")
    if failed:
        print(f"failed files ({len(failed)}): {failed}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python scripts/precompute.py /path/to/audio/folder")
        sys.exit(1)
    main(sys.argv[1])