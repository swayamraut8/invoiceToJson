from flask import Flask, request, jsonify
import pdfplumber
import re

app = Flask(__name__)

def parse_invoice(pdf_path):
    data = {"seller": {}, "buyer": {}, "invoice": {}, "products": []}

    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    # Extract seller details
    seller_match = re.search(r"Seller:\s*(.+)\nAddress:\s*(.+)\nEmail:\s*(.+)", text)
    if seller_match:
        data["seller"] = {
            "name": seller_match.group(1).strip(),
            "address": seller_match.group(2).strip(),
            "email": seller_match.group(3).strip()
        }

    # Extract buyer details
    buyer_match = re.search(r"Buyer:\s*(.+)\nAddress:\s*(.+)\nEmail:\s*(.+)", text)
    if buyer_match:
        data["buyer"] = {
            "name": buyer_match.group(1).strip(),
            "address": buyer_match.group(2).strip(),
            "email": buyer_match.group(3).strip()
        }

    # Extract invoice details
    invoice_match = re.search(r"Invoice No:\s*(\S+)\nDate:\s*(\d{4}-\d{2}-\d{2})", text)
    if invoice_match:
        data["invoice"] = {
            "invoice_no": invoice_match.group(1).strip(),
            "date": invoice_match.group(2).strip()
        }

    # Extract product details
    product_lines = re.findall(r"([\w\s]+)\s+(\d+)\s+\$(\d+\.\d{2})\s+\$(\d+\.\d{2})", text)
    for prod in product_lines:
        data["products"].append({
            "name": prod[0].strip(),
            "quantity": int(prod[1]),
            "unit_price": float(prod[2]),
            "total_price": float(prod[3])
        })

    return data

@app.route("/upload", methods=["POST"])
def upload_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    pdf_path = f"./{file.filename}"
    file.save(pdf_path)

    parsed_data = parse_invoice(pdf_path)
    return jsonify(parsed_data)

if __name__ == "__main__":
    app.run(debug=True)
