import streamlit as st
import json


def get_plan_query(k, data):
    return "\n".join(data.get(k, {}).get('translations', []))


# Load the JSON file
@st.cache_data
def load_documents(json_file):
    with open(json_file, 'r') as f:
        documents = json.load(f)
    return documents


# Save the answers to a JSON file
def save_answers(answers, output_file):
    with open(output_file, 'w') as f:
        json.dump(answers, f, indent=4)


# Main function to run the Streamlit app
def main():
    st.title("Document Q&A App")

    # Load documents
    json_file = '../../data/HTML_query_results.json'  # Replace with your JSON file path
    documents = load_documents(json_file)

    # Initialize session state for answers if not already done
    if 'answers' not in st.session_state:
        st.session_state.answers = {}

    # Dropdown to select a document
    doc_index = st.selectbox("Select a document", list(documents.keys()))

    # Display the selected document
    st.markdown("### Document Content")
    st.markdown(documents[doc_index])

    # Define questions (you can customize these)
    questions = [
        "What is the main topic of the document?",
        "What are the key points mentioned?",
        "What is your overall impression of the document?"
    ]

    # Display questions and store answers
    st.markdown("### Questions")
    for i, question in enumerate(questions):
        answer = st.text_area(f"Q{i+1}: {question}", key=f"{doc_index}_q{i}")
        st.session_state.answers[f"{doc_index}_q{i}"] = answer

    # Save answers to a JSON file
    if st.button("Save Answers"):
        save_answers(st.session_state.answers, 'answers.json')
        st.success("Answers saved successfully!")

if __name__ == "__main__":
    main()

# with app.state:
#     current_document_index = 0
#     current_document = data.get(str(current_document_index), "")
#     questions = [
#         "Does the land use plan need explitation plan?",
#         "Is there an exploitation plan made for this land use plan?",
#     ]
#     answers = ["" for _ in questions]

