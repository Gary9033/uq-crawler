from flask import Flask, render_template, request , redirect
from main import uq_crawl 
from watchlist import add_to_watchlist, load_watchlist, remove_from_watchlist, is_subscribed

app = Flask(__name__)

@app.route("/subscribe", methods=["POST"])
def subscribe():
    model = request.form.get("model")
    brand = request.form.get("brand")
    name  = request.form.get("name")
    url   = request.form.get("url")
    success = add_to_watchlist(model, brand, name, url)
    status = "already" if not success else "ok"
    return redirect(f"/?subscribed={status}&model={model}&brand={brand}")

@app.route("/unsubscribe", methods=["POST"])
def unsubscribe():
    model = request.form.get("model")
    brand = request.form.get("brand")
    remove_from_watchlist(model, brand)
    return redirect(f"/?model={model}&brand={brand}")

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    model = request.args.get("model", "")
    brand = request.args.get("brand", "uniqlo")
    subscribed_status = request.args.get("subscribed", None)

    # 判斷目前查詢的商品是否已訂閱
    already_subscribed = is_subscribed(model, brand) if model else False

    if request.method == "POST":
        model = request.form.get("model", "").strip()
        brand = request.form.get("brand", "uniqlo")
        already_subscribed = is_subscribed(model, brand)
        if model:
            result = uq_crawl(model, brand)
            if "error" in result:
                error = result["error"]
                result = None

    if request.method == "GET" and model and not result:
        result = uq_crawl(model, brand)
        if "error" in result:
            error = result["error"]
            result = None

    return render_template("index.html",
        result=result,
        error=error,
        model=model,
        brand=brand,
        already_subscribed=already_subscribed,
        subscribed_status=subscribed_status
    )

if __name__ == "__main__":
    app.run(debug=True)
