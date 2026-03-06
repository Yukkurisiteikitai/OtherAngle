python -m venv Sample_Venv
Sample_Venv\Scripts\activate
pip install -r requirements.txt
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
python Model_install.py