import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pymupdf
import io
import math
import secrets
import string
from st_copy_to_clipboard import st_copy_to_clipboard
from datetime import datetime

# Note : use 
# pyinstaller --noconsole --clean --collect-all streamlit --collect-all PIL --collect-all pymupdf --collect-all st_copy_to_clipboard run.py
# to build the binaries for the GitHub release. The --noconsole flag is important to avoid a console window popping up on Windows.
# The rename dist/run.exe as dist/FiligraneMalin.exe and ensure this app is copied alongside it before zipping and releasing.

st.set_page_config(
    page_title="Filigrane Malin",
    page_icon="🦊",
    layout="wide",  # Uses full screen width
    initial_sidebar_state="expanded"
)

# Custom CSS to set the sidebar width to 525px
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 525px !important;
            min-width: 525px !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)
st.info("🛡️ **Confidentialité garantie :** Cette application fonctionne 100% hors-ligne. Aucun document ou information ne quitte votre ordinateur durant son utilisation.")


def generate_secure_password(length=16):
    """Generates a cryptographically secure password based on Bitwarden defaults."""
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    special = "!@#$%^&*"
    all_chars = lower + upper + digits + special
    
    # Ensure the password contains at least one character from each category
    while True:
        pwd = ''.join(secrets.choice(all_chars) for _ in range(length))
        if (any(c in lower for c in pwd) and
            any(c in upper for c in pwd) and
            any(c in digits for c in pwd) and
            any(c in special for c in pwd)):
            return pwd

def estimate_crack_time(password):
    """Estimates brute force time (100 billion hashes/sec) and returns a UI progress score."""
    if not password:
        return 0.0, ""
    
    # Calculate available character pool size
    charset = 0
    if any(c.islower() for c in password): charset += 26
    if any(c.isupper() for c in password): charset += 26
    if any(c.isdigit() for c in password): charset += 10
    if any(c in "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~ " for c in password): charset += 32
    
    if charset == 0: return 0.0, ""
    
    # Combinations = pool size ^ password length
    combinations = charset ** len(password)
    crack_time_seconds = combinations / 100_000_000_000
    
    # Convert to human-readable thresholds and Streamlit progress bar scores (0.0 to 1.0)
    if crack_time_seconds < 1: return 0.1, "Instantané ❌"
    elif crack_time_seconds < 60: return 0.1, f"{int(crack_time_seconds)} secondes ❌"
    elif crack_time_seconds < 3600: return 0.2, f"{int(crack_time_seconds / 60)} minutes ❌"
    elif crack_time_seconds < 86400: return 0.3, f"{int(crack_time_seconds / 3600)} heures ❌"
    elif crack_time_seconds < 31_536_000: return 0.5, f"{int(crack_time_seconds / 86400)} jours ⚠️"
    elif crack_time_seconds < 31_536_000: return 0.6, f"{int(crack_time_seconds / 2_592_000)} mois ⚠️"
    elif crack_time_seconds < 31_536_000 * 100: return 0.8, f"{int(crack_time_seconds / 31_536_000)} ans ✅"
    else: return 1.0, "+ de 1000 ans 🛡️"

def draw_colored_progress_bar(score):
    """Draws a custom HTML progress bar that changes color based on the score."""
    # Convert the 0.1 - 1.0 score into a percentage for the CSS width
    percentage = int(score * 100)
    # Traffic light color logic
    if score <= 0.2:
        color = "#FF4B4B"  # Red (Instantané / Secondes / Minutes)
    elif score <= 0.4:
        color = "#FF9029"  # Orange (Heures / Jours)
    elif score <= 0.6:
        color = "#FFD13B"  # Yellow (Mois)
    elif score <= 0.8:
        color = "#00C04B"  # Light Green (Années)
    else:
        color = "#078B38"  # Dark Green (+ de 1000 ans)
    # Build the HTML/CSS
    progress_html = f"""
    <div style="width: 100%; background-color: #e6e6e6; border-radius: 5px; margin-top: 5px; margin-bottom: 15px;">
        <div style="width: {percentage}%; height: 12px; background-color: {color}; border-radius: 5px; transition: width 0.4s ease-in-out;"></div>
    </div>
    """
    # Render it in Streamlit
    st.markdown(progress_html, unsafe_allow_html=True)



# Initialize session state variables to persist generated results
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None
if "pdf_filename" not in st.session_state:
    st.session_state.pdf_filename = "filigrane_document.pdf"

# Sidebar controls
st.sidebar.markdown(
    """
    <div style="font-size: 46px; font-weight: 800; text-align: center; width: 100%; margin-bottom: 15px;">
        🦊 Filigrane Malin
    </div>
    """, 
    unsafe_allow_html=True
)
st.sidebar.markdown(
    "Sécurisez vos documents personnels <span style='color: #E63946;'>AVANT</span> qu'ils ne quittent votre PC !", 
    unsafe_allow_html=True
)

st.sidebar.markdown("## Étape 1 - Personnalisez votre filigrane")
today_str = datetime.now().strftime("%d/%m/%Y")
default_text = f"Document fourni le {today_str} exclusivement à [Nom de l'organisme]"
watermark_text = st.sidebar.text_input("Texte (maxi. 100 caractères)", value=default_text, max_chars=100)

# Create 4 columns: Size (2), Color 1 (1), Color 2 (1)
col_size, col_c1, col_c2 = st.sidebar.columns([2, 1, 1], vertical_alignment="bottom")

with col_size:
    font_size = st.slider("Taille de police", min_value=12, max_value=48, value=24)

with col_c1:
    # Original Blue
    color1_hex = st.color_picker("Couleurs alternées", value="#14285A") 

with col_c2:
    # Original Red
    color2_hex = st.color_picker("", value="#E63946")

# Initialize the angle in the session state (default to 45)
if "watermark_angle" not in st.session_state:
    st.session_state.watermark_angle = 45

# Define a tiny callback function to update the angle
def set_angle(new_angle):
    st.session_state.watermark_angle = new_angle

# The slider, tied directly to the buttons via the "key" parameter
angle = st.sidebar.slider(
    "Orientation du texte", 
    min_value=-90, 
    max_value=90, 
    key="watermark_angle" 
)

# Build the 4 horizontal buttons for orientation
col1, col2, col3, col4 = st.sidebar.columns(4)

with col1:
    st.button("― 0°", on_click=set_angle, args=(0,), use_container_width=True, help="Horizontale")
with col2:
    st.button("⟋ 45°", on_click=set_angle, args=(45,), use_container_width=True, help="Diagonale droite")
with col3:
    st.button("⏐ 90°", on_click=set_angle, args=(90,), use_container_width=True, help="Verticale")
with col4:
    st.button("⟍ -45°", on_click=set_angle, args=(-45,), use_container_width=True, help="Diagonale gauche")

# Map intuitive labels to the mathematical intensity values
wave_options = {
    "― Aucune": 0,
    "~ Légère": 5,
    "∿ Moyenne": 12,
    "༄ Forte": 20
}

# Create a horizontal radio button group
selected_wave = st.sidebar.radio(
    "Ondulation du texte",
    options=list(wave_options.keys()),
    index=1,  # Default to "Light"
    horizontal=True
)

# Extract the actual integer value for the Pillow image generation function
wave_intensity = wave_options[selected_wave]

transparency_percent = st.sidebar.slider("Transparence du texte (%)", min_value=0, max_value=100, value=65)
opacity_percent = 100 - transparency_percent
opacity = int((opacity_percent / 100.0) * 255)

st.sidebar.markdown("---")
st.sidebar.markdown("💡 [Comment choisir un bon mot de passe ? (Guide CNIL)](https://www.cnil.fr/fr/les-conseils-de-la-cnil-pour-un-bon-mot-de-passe)")
st.sidebar.markdown("💡 [Combien de temps un pirate met-il pour trouver votre mot de passe ? (Le Magazine du Numérique)](https://www.francenum.gouv.fr/magazine-du-numerique/combien-de-temps-un-pirate-met-il-pour-trouver-votre-mot-de-passe-comment)")

def create_watermarked_image(image, text, size, rot_angle, wave_amp, alpha, hex1, hex2):
    base = image.convert("RGBA")
    
    # Standard A4 width reference benchmark (approx 1240px at standard render density)
    a4_ref_width = 1240.0
    scale_factor = min(1.0, base.width / a4_ref_width)
    
    # Automatically scale down font size and wave intensity for smaller documents
    effective_size = max(12, int(size * scale_factor))
    effective_wave_amp = max(1, int(wave_amp * scale_factor))
    
    # Create an oversized square canvas to prevent any edge clipping during rotation
    max_dim = int(math.hypot(base.width, base.height))
    large_size = max_dim * 2
    large_layer = Image.new("RGBA", (large_size, large_size), (255, 255, 255, 0))
    
    try:
        font = ImageFont.truetype("arial.ttf", effective_size)
    except IOError:
        font = ImageFont.load_default()

    d = ImageDraw.Draw(large_layer)
    
    # Create a long repeating text string that spans the large canvas
    sample_text = text + "     "
    sample_width = font.getlength(sample_text)
    repeats = int((large_size * 2) / sample_width) + 3
    row_text = sample_text * repeats
    
    txt_height = effective_size * 1.8
    y_step = int(txt_height * 2.5)
    
    start_y = -large_size // 2
    end_y = large_size + (large_size // 2)
    
    # Convert Hex 1 to RGB
    h1 = hex1.lstrip('#')
    r1, g1, b1 = tuple(int(h1[i:i+2], 16) for i in (0, 2, 4))

    # Convert Hex 2 to RGB
    h2 = hex2.lstrip('#')
    r2, g2, b2 = tuple(int(h2[i:i+2], 16) for i in (0, 2, 4))

    row_indices = list(range(start_y, end_y, y_step))
    for row_idx, y in enumerate(row_indices):
        current_x = -large_size // 2
        
        # Alternate between Color 1 and Color 2 line-by-line
        row_color = (r1, g1, b1, alpha) if row_idx % 2 == 0 else (r2, g2, b2, alpha)
        
        for i, char in enumerate(row_text):
            char_y = y + int(effective_wave_amp * math.sin((current_x + large_size) / 60.0))
            
            # Draw drop shadow
            d.text((current_x + 3, char_y + 3), char, font=font, fill=(0, 0, 0, int(alpha * 0.5)))
            
            # Draw main text using the uniform row color
            d.text((current_x, char_y), char, font=font, fill=row_color)
            
            current_x += font.getlength(char)

    # Rotate the large canvas smoothly around its center
    rotated_large = large_layer.rotate(rot_angle, resample=Image.BICUBIC, center=(large_size / 2, large_size / 2))
    
    # Crop the exact center region matching document dimensions using integer math
    crop_left = int((large_size - base.width) / 2)
    crop_top = int((large_size - base.height) / 2)
    cropped_txt = rotated_large.crop((crop_left, crop_top, crop_left + base.width, crop_top + base.height))
    
    # Force exact dimension match to prevent alpha_composite size mismatch errors
    if cropped_txt.size != base.size:
        cropped_txt = cropped_txt.resize(base.size, Image.Resampling.BICUBIC)
    
    # Composite over original image
    watermarked = Image.alpha_composite(base, cropped_txt)
    return watermarked.convert("RGB")

# Main 2-column layout to avoid scrolling (Above the fold)
col_left, col_right = st.columns(2, gap="medium")

with col_left:
    st.markdown("##### 📁 Étape 2 - Sélectionnez le document à sécuriser")
    uploaded_file = st.file_uploader(
        label="Formats acceptés: PDF, PNG, JPG (20Mo max)", 
        type=["pdf", "png", "jpg", "jpeg"],
        label_visibility="visible",
        help="Glissez-déposez votre document ici ou cliquez 'Upload'"
    )
    
    # Help section for office document formats tucked neatly below
    with st.expander(icon="❓", label="Vous avez un document Microsoft Word (.docx), Apple Pages (.pages) ou LibreOffice/OpenOffice (.odt)"):
        st.markdown("""
    **Filigrane Malin** n'accepte pas directement ces formats. Aucun téléchargement supplémentaire n'est nécessaire pour convertir votre fichier, vous pouvez simplement utiliser les fonctions intégrées à votre ordinateur :
    * **Sur Microsoft Word / LibreOffice :** Allez dans `Fichier` > `Enregistrer sous` > Choisissez le format **PDF**.
    * **Sur Apple Pages :** Allez dans `Fichier` > `Exporter vers` > **PDF**.
    * **Alternative universelle :** Faites `Ctrl+P` (ou `Cmd+P` sur Mac) pour ouvrir le menu d'impression, et choisissez **"Imprimer en PDF"** ou **"Enregistrer au format PDF"**.
    
    Une fois le PDF sauvegardé, sélectionnez-le ci-dessus !
    """)

with col_right:
    st.markdown("##### 🔏 Étape 3 (facultative) - Ajouter un mot de passe ")
    
    # Initialize password state
    if "pdf_password" not in st.session_state:
        st.session_state.pdf_password = ""
        
    # Variable to track password origin (auto-generated vs manual)
    if "is_auto_generated" not in st.session_state:
        st.session_state.is_auto_generated = False
        
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
     
    pdf_password = st.text_input(
        "Mot de passe",
        value=st.session_state.pdf_password,
        type="password",
        placeholder="Saisissez un mot de passe et appuyez sur '↵ Entrée' au clavier ou cliquez sur «🎲 Générer »",
        label_visibility="visible",
        help="**Format recommandé :** minimum 16 caractères avec au moins 1 minuscule, 1 majuscule, 1 chiffre & 1 caractère spécial (!@#$%^&*)... ou cliquez sur «🎲 Générer » pour un mot de passe sécurisé."
    )

    # Detect manual entry (password changed without using our button)
    if pdf_password != st.session_state.pdf_password:
        st.session_state.is_auto_generated = False

    if st.button("🎲 Générer"):
        if uploaded_file is None:
            st.warning("⚠️ Veuillez d'abord sélectionner un document à sécuriser !")
        else:
            st.session_state.pdf_password = generate_secure_password(16)
            st.session_state.is_auto_generated = True  # Flag as secure auto-generated password
            st.rerun()
            
    st.session_state.pdf_password = pdf_password

    # Display password strength if provided
    if pdf_password:
        if uploaded_file is None:
            st.warning("⚠️ Veuillez d'abord sélectionner un document à sécuriser !")
        else:
            # Show cracking info and warnings only if the document has NOT been generated yet
            if st.session_state.pdf_bytes is None:
                # Show anti-recycling warning only if the user typed their own password manually
                if not st.session_state.is_auto_generated:
                    st.warning(
                        "**Avez-vous déjà utilisé ce mot de passe ailleurs ?**\n\n"
                        "Si oui, rendez-vous service, cliquez sur «🎲 Générer » !", 
                        icon="🕵️"
                    )
                else:
                    st.success("✨ Mot de passe sécurisé généré avec succès !")

                # Security metrics, crack time
                score, time_text = estimate_crack_time(pdf_password)
                draw_colored_progress_bar(score)
                st.markdown(f"**Temps de piratage estimé*:** `{time_text}`")
                st.caption("**Estimation du temps de piratage par « force brute » sur la base de 100 milliards de combinaisons testées par seconde*")
            
            # Copy button remains available always when password is provided
            st_copy_to_clipboard(
                text=pdf_password, 
                before_copy_label="⧉ Copier le mot de passe", 
                after_copy_label="✅ Copié !"
            )

# Automatically invalidate cache if any input settings or parameters change
current_settings = (
    watermark_text,
    font_size,
    color1_hex,
    color2_hex,
    angle,
    wave_intensity,
    opacity,
    pdf_password
)

if "prev_settings" not in st.session_state:
    st.session_state.prev_settings = current_settings

if current_settings != st.session_state.prev_settings:
    st.session_state.prev_settings = current_settings
    st.session_state.pdf_bytes = None  # Clear old generated bytes to force a fresh regeneration

# Track uploaded file changes to clear old results automatically
if "last_uploaded_name" not in st.session_state:
    st.session_state.last_uploaded_name = None

if uploaded_file is not None:
    # If a new file is uploaded, clear previous generated bytes
    if uploaded_file.name != st.session_state.last_uploaded_name:
        st.session_state.last_uploaded_name = uploaded_file.name
        st.session_state.pdf_bytes = None
        
    file_extension = uploaded_file.name.split(".")[-1].lower()
    st.markdown("---")

    if not watermark_text.strip():
        st.error("⚠️ Veuillez saisir un texte pour le filigrane (Étape 1) avant de générer le document.")
    
    elif st.button("🪄 Étape 4 - Générez votre document sécurisé", type="primary"):
        with st.spinner("Application du filigrane et génération du PDF..."):
            output_pdf = pymupdf.open()
            
            if file_extension in ["png", "jpg", "jpeg"]:
                image = Image.open(uploaded_file)
                watermarked_img = create_watermarked_image(image, watermark_text, font_size, angle, wave_intensity, opacity, color1_hex, color2_hex)
                
                img_byte_arr = io.BytesIO()
                watermarked_img.save(img_byte_arr, format='JPEG')
                img_bytes = img_byte_arr.getvalue()
                
                new_page = output_pdf.new_page(width=image.width, height=image.height)
                new_page.insert_image(new_page.rect, stream=img_bytes)
                
            elif file_extension == "pdf":
                pdf_document = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
                for page_num in range(len(pdf_document)):
                    page = pdf_document[page_num]
                    pix = page.get_pixmap(dpi=150)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    
                    watermarked_img = create_watermarked_image(img, watermark_text, font_size, angle, wave_intensity, opacity, color1_hex, color2_hex)
                    
                    img_byte_arr = io.BytesIO()
                    watermarked_img.save(img_byte_arr, format='JPEG')
                    img_bytes = img_byte_arr.getvalue()
                    
                    new_page = output_pdf.new_page(width=page.rect.width, height=page.rect.height)
                    new_page.insert_image(new_page.rect, stream=img_bytes)
            
            save_options = {}
            if pdf_password:
                save_options = {
                    "encryption": pymupdf.PDF_ENCRYPT_AES_128,
                    "user_pw": pdf_password,
                    "owner_pw": pdf_password
                }
            
            base_name = ".".join(uploaded_file.name.split(".")[:-1])
            st.session_state.pdf_bytes = output_pdf.tobytes(**save_options)
            st.session_state.pdf_filename = f"filigrane_{base_name}.pdf"
            st.rerun()

    # Display success and download button ONLY after generation button is clicked
    if st.session_state.pdf_bytes is not None:
        if pdf_password:
            st.success(f"🥂 Votre document sécurisé '{st.session_state.pdf_filename}' est prêt ! Vous pourrez en modifier le nom à l'étape suivante.")
            st.info(
                            "💡 **Conseil :** Assurez-vous d'avoir sauvegardé le mot de passe dans un endroit sûr, comme par exemple "
                            "un [gestionnaire de mots de passe](https://www.francenum.gouv.fr/guides-et-conseils/protection-contre-les-risques/cybersecurite/pourquoi-et-comment-utiliser-un) avant de fermer cette application."
                        )
            st.warning(
                "🚨 **Attention !** Ne transmettez pas le mot de passe dans le même e-mail "
                "que votre document ! Utilisez un autre canal (SMS, WhatsApp...) ou un e-mail séparé."
            )
        else:
            st.success(f"🥂 Votre document sécurisé '{st.session_state.pdf_filename}' est prêt ! Vous pourrez en modifier le nom à l'étape suivante.")
            
        st.download_button(
            label="💾 Étape 5 - Sauvegardez votre document sécurisé",
            data=st.session_state.pdf_bytes,
            file_name=st.session_state.pdf_filename,
            mime="application/pdf"
        )