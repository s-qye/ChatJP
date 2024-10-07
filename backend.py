import openai
import langchain
from langchain.chains import RetrievalQA
from langchain_openai import OpenAI
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma



loader = TextLoader("/Users/sqye/Desktop/Chat_JP/data/jps_student_handbook_2024.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)
embeddings = OpenAIEmbeddings(openai_api_key="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")

docsearch = Chroma.from_documents(texts, embeddings)

qa = RetrievalQA.from_chain_type(llm=OpenAI(openai_api_key="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"), chain_type="stuff", retriever=docsearch.as_retriever(), return_source_documents=True)

def chatjp_ask(query):
    result = qa.invoke({"query": query})
    answer = result["result"]
    return answer

# Flask/SQL stuff
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the SQLAlchemy part of the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://sqye:Tianhao24@localhost/chatjp_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy object with the Flask app
db = SQLAlchemy(app)

# Define the questioning model (table)
class questioning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    advice = db.Column(db.Text)

# Route to display the form and all answered questions
@app.route('/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the question input from the HTML form
        question = request.form['question']

        # Answer the question
        try:
            answers = chatjp_ask(question)
            answer = answers
        except Exception as e:
            answer = "Error occurred during answering mb."
            print(e)  # Log the error

        # Store the original note and its summary in the database
        new_question = questioning(original_question=question, answer=answer, advice=None)
        db.session.add(new_question)
        db.session.commit()

        return redirect(url_for('index'))

    # Query the database for all answered questions
    questions = questioning.query.all()

    # Render the HTML template and pass the notes to it
    return render_template('index.html', questions=questions)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This will create the tables
    app.run(debug=True)
