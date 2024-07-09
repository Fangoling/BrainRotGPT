import chainlit as cl
from chainlit.types import AskFileResponse
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model_name="gpt-4o", temperature=0, streaming=True, base_url="https://llmproxy.meingpt.com")

welcome_message = """Bitte laden Sie eine VTT-Datei hoch"""
@cl.on_chat_start
async def start():
    files = None
    while files is None:
        files = await cl.AskFileMessage(
            content=welcome_message,
            accept=["text/vtt"],
            max_size_mb=20,
            timeout=180,
        ).send()

    file = files[0]

    msg = cl.Message(content=f"Processing `{file.name}`...")
    await msg.send()

    # Read the content of the VTT file
    with open(file.path, 'r', encoding='utf-8') as f:
        meeting_content = f.read()

    # Let the user know that the system is ready
    msg.content = f"`{file.name}` processed and content stored in variable."
    await msg.update()

    cl.user_session.set("meeting_content", meeting_content)
    print(meeting_content)

    # Request a summary from the LLM
    summary_response = llm.invoke(
        [
        ("system", "You are an assistant who summarizes the content of a video conference.The summary should include only important and business-relevant information, filtering out any trivial details such as someone getting coffee or clearing their throat. The summary should be concise and long enough to take about 30 seconds to read aloud. Der Text soll auf deutsch sein und fließend."),
        ("human", f"Please summarize the following meeting transcript. :\n\n{meeting_content}")
    ]
    )

    summary = summary_response.content
    print(summary)

    # Send the summary to the user
    await cl.Message(content=f"Meeting Summary:\n\n{summary}").send()


