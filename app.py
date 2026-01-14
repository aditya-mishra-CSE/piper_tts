import uuid
import streamlit as st
# from backend.tts_piper import PiperTTS
from backend.tts_piper_cli import PiperTTS

from backend.state import parse_dialogue, extract_ai_text
from backend.graph import chatbot
from langchain_core.messages import HumanMessage

# ---------- INIT ----------
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- TTS ----------
# male_tts = PiperTTS("models/en_US-lessac-low.onnx")
# female_tts = PiperTTS("models/en_US-lessac-low.onnx")
# ---------- TTS (Piper CLI) ----------
PIPER_DIR = r"C:\Users\aditya.mishra01\Downloads\piper"

male_tts = PiperTTS(
    piper_dir=PIPER_DIR,
    model_path=r"C:\Users\aditya.mishra01\Downloads\piper\hi_IN-pratham-medium.onnx",
)

female_tts = PiperTTS(
    piper_dir=PIPER_DIR,
    model_path=r"C:\Users\aditya.mishra01\Downloads\piper\hi_IN-priyamvada-medium.onnx",
)


import base64
import streamlit.components.v1 as components


def autoplay_audio_sequence(audio_bytes_list):
    """
    Plays multiple WAV audios sequentially without showing UI.
    """
    audio_tags = []

    for audio_bytes in audio_bytes_list:
        b64 = base64.b64encode(audio_bytes).decode()
        audio_tags.append(f"data:audio/wav;base64,{b64}")

    js = f"""
    <script>
    const audioSources = {audio_tags};
    let index = 0;

    function playNext() {{
        if (index >= audioSources.length) return;

        const audio = new Audio(audioSources[index]);
        audio.onended = () => {{
            index++;
            playNext();
        }};
        audio.play();
    }}

    playNext();
    </script>
    """

    components.html(js, height=0)



# def speak_dialogue(dialogue):
#     for speaker, text in dialogue:
#         audio = male_tts.synthesize(text) if speaker == "Speaker A" else female_tts.synthesize(text)
#         st.audio(audio, format="audio/wav")

def speak_dialogue(dialogue):
    audio_queue = []

    for speaker, text in dialogue:
        tts = male_tts if speaker == "Speaker A" else female_tts
        audio = tts.synthesize(text)
        audio_queue.append(audio)

    autoplay_audio_sequence(audio_queue)


# ---------- UI ----------
st.title("🤖 Two-Speaker Conversational AI (Offline TTS)")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask something...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    response = chatbot.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config={"configurable": {"thread_id": st.session_state.thread_id}},
    )

    raw_content = response["messages"][-1].content
    ai_text = extract_ai_text(raw_content)

    
    st.session_state.messages.append({"role": "assistant", "content": ai_text})

    with st.chat_message("assistant"):
        st.markdown(ai_text)

    dialogue = parse_dialogue(ai_text)
    if dialogue:
        speak_dialogue(dialogue)
