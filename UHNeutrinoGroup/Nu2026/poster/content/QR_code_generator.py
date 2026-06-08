import qrcode

# 1. Define the DOI target link
url = "https://doi.org/10.48550/arXiv.2603.03561"

# 2. Configure the QR code properties
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_M,  # Medium error correction
    box_size=10,
    border=4,
)
qr.add_data(url)
qr.make(fit=True)

# 3. Create and save the QR code image
img = qr.make_image(fill_color="black", back_color="white")
filename = "ArXiV_QR_code.png"
img.save(filename)

print(f"✨ QR code successfully generated and saved as '{filename}'!")
filename = "ArXiV_citation.md"
with open(filename, "w") as f:
    f.write("="*50 + "\n")
    f.write("CITATION INFORMATION:\n")
    f.write("="*50 + "\n")
    f.write(
        "Crow, B. C., Dornfest, M. A. A., Learned, J. G., Seligman, J. D., "
        "Sibert, N. S., Yepez, J. G., & Li, V. A. (2026). Enhancing Angular "
        "Sensitivity of Segmented Antineutrino Detectors for Reactor Monitoring "
        "Applications. arXiv:2603.03561. "
        "https://doi.org/10.48550/arXiv.2603.03561 \n"
    )
    f.write("="*50 + "\n")
print(f"📄 Citation information written to '{filename}'!")
