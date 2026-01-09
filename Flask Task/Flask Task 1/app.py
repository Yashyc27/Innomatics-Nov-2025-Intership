import base64
from flask import Flask, render_template, request

app = Flask(__name__)

class TextProcessor:
    """A custom class to handle string transformations uniquely."""
    @staticmethod
    def process_data(raw_input):
        if not raw_input:
            return "No Data", "00", "None"
            
        shouting = raw_input.upper()
        
        hex_output = raw_input.encode('utf-8').hex().upper()
        
        b64_bytes = base64.b64encode(raw_input.encode('utf-8'))
        web_encoded = b64_bytes.decode('utf-8')
        
        return shouting, hex_output, web_encoded

@app.route('/')
def main_entry():
    query_val = request.args.get('name', 'User')
    
    caps, hex_val, b64_val = TextProcessor.process_data(query_val)
    
    return render_template(
        'index.html',
        input_name=query_val,
        caps_name=caps,
        hex_name=hex_val,
        b64_name=b64_val
    )

if __name__ == '__main__':
    app.run(debug=True)