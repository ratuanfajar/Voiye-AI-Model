"""Model conversion runner script"""

from src.vision.exporter import convert_pt_to_tflite


def main():
    convert_pt_to_tflite("models/angkot.pt", "models/angkot.tflite")

if __name__ == "__main__":
    main()
