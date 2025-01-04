import re
import streamlit as st
from openai import OpenAI

openai_api_key = None
assistant_id = "asst_1YBB5MbnJ3OVGQm6FFbWLRxR"
client = OpenAI(api_key=openai_api_key)
assistant = client.beta.assistants.retrieve(
    assistant_id=assistant_id,
)

thread = client.beta.threads.create()

questions: list[str] = [
    # Leadership and Governance
    "Who is the tribal president of the Mescalero Apache Tribe?",
    "What roles do tribal council members play?",
    "How is leadership structured within the Mescalero Apache Tribe's administration?",
    "What measures prevent natural resource regulation violations on the reservation?",
    
    # Cultural Preservation
    "What cultural ceremonies are important to the Mescalero Apache people?",
    "How does the tribe promote cultural education among younger generations?",
    "How does preserving the Apache language affect community identity?",
    "What are the objectives of the Mescalero Apache Tribe's language program?",
    
    # Education and Youth Development
    "What partnerships enhance education and youth development programs?",
    "How are contemporary challenges reflected in educational curricula and community programs?",
    
    # Health and Social Services
    "What mental health services does the Mescalero System of Care provide?",
    "How does the tribe address health disparities through the Community Health Representative Program?",
    
    # Economic and Ecological Initiatives
    "How does the Tribal Fish Hatchery support economic and ecological initiatives?",
    "What criteria are required for a gaming license from the Tribal Gaming Commission?",
    "How does the tribe ensure confidentiality in gaming license background investigations?",
]

st.title("Mescalero Chatbot")
st.caption("Interact with a chatbot to learn about the Mescalero Apache Tribe.")

prompt = None
st.subheader("📚 Choose or Type a Question")
question = st.selectbox("Predefined Questions:", [""] + questions)
if st.button("Ask") and question:
    prompt = question

st.title('')
st.subheader("💬 Chatbot")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I assist you?"}]


for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])
custom_question = st.chat_input("Ask your own question:")
prompt = custom_question if not prompt else prompt

if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    try:
        # Send the question to the thread
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt,
        )
        # Execute the thread
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )
        if run.status == 'completed': 
            # Retrieve the run result
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
        )
            # Get the last message from the thread which is assumed to be the answer
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )

            last_message = messages.data[0]
            response = last_message.content[0].text.value
            regex = r'【\d:\d†[A-Za-z]+】'
            matches = re.findall(regex, response)
            if matches:
                for match in matches:
                    response = response.replace(match, "").replace("  ", " ")
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)
    except Exception as e:
        st.error(f"Error: {e}")