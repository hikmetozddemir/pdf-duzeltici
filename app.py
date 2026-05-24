import streamlit as st
import fitz
import google.generativeai as genai
import os

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="NEON PDF | Kusursuz Düzeltici", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 🚀 AGRESİF CSS VE ANİMASYON TASARIMI 🚀 ---
st.markdown("""
<style>
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 50%, #111 0%, #000 100%);
        color: #e0e0e0;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .glitch-baslik {
        font-family: 'Courier New', Courier, monospace;
        color: #00ffcc;
        text-align: center;
        font-weight: 900;
        font-size: 4.5rem;
        margin-top: -30px;
        margin-bottom: 5px;
        text-transform: uppercase;
        letter-spacing: 5px;
        text-shadow: 0 0 10px #00ffcc, 0 0 20px #00ffcc, 0 0 40px #00ffcc;
        border-bottom: 2px solid #00ffcc;
        padding-bottom: 20px;
    }
    
    .alt-baslik {
        color: #a0a0a0;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 40px;
        font-family: Arial, sans-serif;
        letter-spacing: 2px;
    }

    .stFileUploader {
        background-color: rgba(0, 255, 204, 0.05);
        border: 2px dashed #00ffcc;
        border-radius: 15px;
        padding: 20px;
    }
    
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #ff0055, #00ffcc);
        color: #fff;
        border: none;
        border-radius: 8px;
        padding: 20px;
        font-size: 24px;
        font-weight: 900;
        box-shadow: 0 0 20px rgba(255, 0, 85, 0.6), 0 0 40px rgba(0, 255, 204, 0.6);
        transition: all 0.2s ease-in-out;
        width: 100%;
        text-transform: uppercase;
        cursor: pointer;
    }
    
    div.stButton > button:first-child:hover {
        transform: scale(1.02);
        box-shadow: 0 0 30px rgba(255, 0, 85, 1), 0 0 60px rgba(0, 255, 204, 1);
        color: white;
    }

    .rapor-kutusu {
        background: #111;
        border-left: 5px solid #ff0055;
        padding: 15px;
        margin-bottom: 10px;
        font-family: monospace;
        font-size: 1.1rem;
        color: #fff;
        box-shadow: inset 0 0 10px rgba(255,0,85,0.2);
    }
    
    .eski-kelime { color: #ff0055; text-decoration: line-through; }
    .yeni-kelime { color: #00ffcc; font-weight: bold; }

    .animasyon-kapsayici {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        z-index: -1;
        overflow: hidden;
        pointer-events: none;
    }
    
    .sembol {
        position: absolute;
        color: rgba(0, 255, 204, 0.15);
        font-size: 3rem;
        animation: yukariKay 20s linear infinite;
        bottom: -10vh;
    }
    
    .sembol:nth-child(1) { left: 10%; animation-duration: 15s; font-size: 5rem; }
    .sembol:nth-child(2) { left: 30%; animation-duration: 25s; animation-delay: 2s; }
    .sembol:nth-child(3) { left: 50%; animation-duration: 18s; font-size: 4rem; animation-delay: 5s;}
    .sembol:nth-child(4) { left: 70%; animation-duration: 22s; animation-delay: 1s; }
    .sembol:nth-child(5) { left: 85%; animation-duration: 12s; font-size: 6rem; animation-delay: 3s;}
    
    @keyframes yukariKay {
        0% { transform: translateY(0) rotate(0deg); }
        100% { transform: translateY(-110vh) rotate(360deg); }
    }
</style>

<div class="animasyon-kapsayici">
    <div class="sembol">📄</div>
    <div class="sembol">⚙️</div>
    <div class="sembol">🛠️</div>
    <div class="sembol">🔍</div>
    <div class="sembol">💻</div>
</div>
""", unsafe_allow_html=True)

# API Anahtarın
genai.configure(api_key="SENIN_API_ANAHTARIN")
model = genai.GenerativeModel('gemini-2.5-flash')

st.markdown("<div class='glitch-baslik'>PDF NEON MOTORU</div>", unsafe_allow_html=True)
st.markdown("<div class='alt-baslik'>[ MİKROSKOBİK SİLME VE KUSURSUZ HİZALAMA AKTİF ]</div>", unsafe_allow_html=True)

if "pdf_data" not in st.session_state:
    st.session_state.pdf_data = None
if "rapor" not in st.session_state:
    st.session_state.rapor = []

FONT_PATHS = {
    "serif": [
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/Library/Fonts/Times New Roman.ttf",
        "C:\\Windows\\Fonts\\times.ttf"
    ],
    "sans": [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "C:\\Windows\\Fonts\\arial.ttf"
    ]
}

def get_font_path(font_type):
    for path in FONT_PATHS[font_type]:
        if os.path.exists(path): return path
    return None

def get_bg_color(page, rect):
    x_sample = max(0, rect.x0 - 5)
    y_sample = max(0, rect.y0 - 5)
    sample_rect = fitz.Rect(x_sample, y_sample, x_sample + 1, y_sample + 1)
    try:
        pix = page.get_pixmap(clip=sample_rect)
        if pix.width > 0 and pix.height > 0:
            return (pix.pixel(0,0)[0]/255, pix.pixel(0,0)[1]/255, pix.pixel(0,0)[2]/255)
    except:
        pass
    return (1, 1, 1)

def get_text_properties(page, word_rect):
    text_dict = page.get_text("dict")
    for block in text_dict.get("blocks", []):
        if block.get("type") == 0:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    span_rect = fitz.Rect(span["bbox"])
                    if span_rect.intersects(word_rect):
                        hex_color = span.get("color", 0)
                        rgb = (((hex_color>>16)&255)/255, ((hex_color>>8)&255)/255, (hex_color&255)/255)
                        font_name = span.get("font", "").lower()
                        
                        is_serif = True
                        if "arial" in font_name or "helv" in font_name or "sans" in font_name:
                            is_serif = False
                            
                        return {
                            "size": span.get("size", 11),
                            "color": rgb,
                            "origin_y": span["origin"][1], # Havadaki harfleri engelleyen KESİN baseline
                            "is_serif": is_serif
                        }
    return {"size": 11, "color": (0.2, 0.2, 0.2), "origin_y": word_rect.y1 - (word_rect.height * 0.2), "is_serif": True}

col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    uploaded_file = st.file_uploader("📂 İŞLENECEK PDF DOSYASINI SEÇİN", type="pdf")

    if uploaded_file is not None:
        st.write("") 
        if st.button("⚡ SİSTEMİ ATEŞLE (Cerrahi Analiz)"):
            with st.spinner("Sistem Verileri Parçalıyor..."):
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                
                serif_path = get_font_path("serif")
                sans_path = get_font_path("sans")

                tum_metin = "".join([page.get_text() for page in doc])

                # AI İÇİN KESİN KISITLAMALAR EKLENDİ
                prompt = f"""
                Aşağıdaki metindeki yazım hatalarını bul. Eş anlamlı kelime KULLANMA.
                ÇOK ÖNEMLİ KURAL: Çıktı SADECE TEK KELİME olmalıdır. Asla iki veya daha fazla kelimeyi yan yana yazma. 
                Örnek Hatalı Çıktı: merhebe benm|merhaba benim
                Örnek Doğru Çıktı: 
                merhebe|merhaba
                benm|benim
                
                Çıktı KESİNLİKLE sadece şu formatta olsun: hatalı|doğru
                Metin:
                {tum_metin}
                """
                
                rapor_listesi = []
                
                try:
                    response = model.generate_content(prompt)
                    
                    duzeltmeler = []
                    for satir in response.text.split('\n'):
                        if "|" in satir:
                            eski, yeni = satir.split("|")
                            # Sadece tek kelimelik düzeltmeleri alarak blok silinmesini engelliyoruz
                            if eski.strip().lower() != yeni.strip().lower() and len(eski.split()) == 1 and len(yeni.split()) == 1:
                                duzeltmeler.append((eski.strip(), yeni.strip()))
                    
                    for page_num, page in enumerate(doc):
                        degisiklik_plani = []
                        
                        for eski, yeni in duzeltmeler:
                            bulunanlar = page.search_for(eski)
                            for inst in bulunanlar:
                                props = get_text_properties(page, inst)
                                bg_color = get_bg_color(page, inst)
                                
                                # ÇÖZÜM BURADA:
                                # Yandaki masum kelimeleri SİLMEMEK için X eksenini 0.8 birim DARALTIYORUZ.
                                # Eski kelimenin gölgesi kalıp SİRRITMASIN diye Y eksenini 1.0 birim GENİŞLETİYORUZ.
                                silme_alani = fitz.Rect(inst.x0 + 0.8, inst.y0 - 1.0, inst.x1 - 0.8, inst.y1 + 1.0)
                                
                                # Orijinal X başlangıç noktasını kaybetmemek için inst.x0'ı plan listesine ekliyoruz
                                degisiklik_plani.append((silme_alani, yeni, props, bg_color, eski, inst.x0))

                        for plan in degisiklik_plani:
                            silme_alani, _, _, bg_color, _, _ = plan
                            annot = page.add_redact_annot(silme_alani)
                            annot.set_colors(stroke=None, fill=bg_color)
                            annot.update()
                        
                        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
                        
                        if serif_path: page.insert_font(fontname="TR_Serif", fontfile=serif_path)
                        if sans_path: page.insert_font(fontname="TR_Sans", fontfile=sans_path)
                        
                        for plan in degisiklik_plani:
                            silme_alani, yeni, props, _, eski, orijinal_x0 = plan
                            f_name = "TR_Serif" if props["is_serif"] else "TR_Sans"
                            if (props["is_serif"] and not serif_path): f_name = "tiro"
                            if (not props["is_serif"] and not sans_path): f_name = "helv"
                            
                            # Yazıyı KESİN olarak orijinal başladığı yerden ve KESİN orijinal boyutuyla başlatıyoruz
                            page.insert_text(
                                (orijinal_x0, props["origin_y"]), 
                                yeni, 
                                fontsize=props["size"],
                                fontname=f_name, 
                                color=props["color"]
                            )
                            
                            rapor_listesi.append((page_num + 1, eski, yeni))
                    
                    st.session_state.pdf_data = doc.tobytes(garbage=4, deflate=True)
                    st.session_state.rapor = rapor_listesi
                    
                except Exception as e:
                    st.error(f"Sistem Hatası: {e}")

if st.session_state.pdf_data:
    st.markdown("---")
    
    col_rapor, col_indir = st.columns([2, 1])
    
    with col_rapor:
        if st.session_state.rapor:
            st.markdown("<h3 style='color: #00ffcc;'>[+] İŞLEM KAYITLARI (LOGS)</h3>", unsafe_allow_html=True)
            unique_rapor = list(dict.fromkeys(st.session_state.rapor))
            for sayfa, eski, yeni in unique_rapor:
                st.markdown(f"""
                <div class="rapor-kutusu">
                    > SAYFA {sayfa} HATA TESPİTİ: <span class="eski-kelime">[{eski}]</span> >> DÜZELTİLDİ: <span class="yeni-kelime">[{yeni}]</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("SİSTEM UYARISI: Hata Bulunamadı.")
            
    with col_indir:
        st.markdown("<h3 style='color: #00ffcc;'>[+] ÇIKTIYI AL</h3>", unsafe_allow_html=True)
        st.download_button(
            label="⬇️ NEON PDF'İ İNDİR",
            data=st.session_state.pdf_data,
            file_name="kusursuz_pdf_neon.pdf",
            mime="application/pdf"
        )