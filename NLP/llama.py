from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Settings,
    load_index_from_storage
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.openai import OpenAI

import os
import warnings
warnings.filterwarnings('ignore')
import os
from dotenv import load_dotenv 

load_dotenv()

def remove_first_and_last(lst):
    return [s[1:-1] if len(s) > 1 else '' for s in lst]
def main_match(user_req, filename):
    # Get the directory of this script
    script_dir = os.path.dirname(__file__)
    # Construct the full path to the file
    file_path = os.path.join(script_dir, filename)

    Settings.llm = OpenAI(model="o1-preview", api_key=os.getenv("OPENAI_API_KEY"))
    Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    Settings.node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=200)

    reader = SimpleDirectoryReader(input_files=[file_path])
    documents = reader.load_data()
    nodes = Settings.node_parser.get_nodes_from_documents(documents, show_progress=True)

    vector_index = VectorStoreIndex.from_documents(documents, node_parser=nodes)
    vector_index.storage_context.persist(persist_dir="storage_mini")
    storage_context = StorageContext.from_defaults(persist_dir="storage_mini")
    index = load_index_from_storage(storage_context)
    query_engine = index.as_query_engine()

    q6 = f""" 
    You are a system that is adept at evaluating and retrieving links from a json file,
    and those links will be retrieved on the basis of the user's specifications and requests,
    i.e., you will receive a user request (for the purpose of making an openapi spec) and you will evaluate that request,
    each word of it. Then, you will use this information to retrieve possible matches from a json file containing links from specific documentation which might contain the information the user is looking for.
    The user request is as follows: {user_req}
    YOUR FINAL OUTPUT SHOULD ONLY CONTAIN A LIST OF THE MATCHES AND NOTHING ELSE, ABSOLUTELY NOTHING ELSE, AND THESE MATCHES SHOULD BE TRACEABLE AND FOUND DIRECTLY, AS IS, IN THE GIVEN JSON FILE. MAKE SURE TO ADHERE TO THESE INSTRUCTIONS.
    I AM REITERATING THAT THE OUTPUT SHOULD BE A COMMA SEPERATED LIST, WITH EACH ELEMENT OF THAT LIST STRICTLY BELONGING TO THE JSON FILE AND BEING AN INDIVIDUAL ELEMENT
    GIVE OUT MAX NUMBER OF POSSIBLE MATCHES, TRIPLE CHECK
    """
    resp6 = query_engine.query(q6)
    list_resp6 = [item.strip() for item in str(resp6).strip("[]").split(",")]
    strings =list_resp6
    result = remove_first_and_last(strings)

    return result

