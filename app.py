from flask import Flask, render_template, request, redirect, flash, url_for, session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Cont, BasketItem, Order, Base
import time
import threading

app = Flask(__name__)
app.secret_key = 'secretkey'

hostname = "127.0.0.1"
username = "root"
password = ""
port = 3306
database = "sistem_comanda_mancare"

DATABASE_URL = f'mysql+pymysql://{username}:{password}@{hostname}:{port}/{database}'

engine = create_engine(DATABASE_URL)
Base.metadata.bind = engine
Session = sessionmaker(bind=engine)
db_session = Session()


@app.route("/homepage")
def home():
    return render_template("homepage.html")



@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = db_session.query(Cont).filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = user.username
            flash("Login successful!", 'success')
            return render_template('homepage.html', logged_in = True, username=username)
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')



@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out!', 'success')
    return redirect(url_for('home'))



@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        existing_user = db_session.query(Cont).filter_by(username=username).first()
        existing_email = db_session.query(Cont).filter_by(email=email).first()

        if not username or not email or not password or not confirm_password:
            flash("Please fill in all the required information!", 'danger')
        elif password != confirm_password:
            flash('Passwords do not match', 'danger')
        elif not email.endswith(".com"):
            flash("Invalid email address!", 'danger')
        elif existing_user:
            flash("Username already exists. Please select another.", 'danger')
        elif existing_email:
            flash("This email is already in use. Please select another one.", 'danger')
        else:
            new_user = Cont(username=username, email=email, password=password)
            db_session.add(new_user)
            db_session.commit()
            flash("Account succesfully registered!", 'success')
            return redirect(url_for("login"))

    return render_template('register.html')


@app.route("/menu", methods=['GET', 'POST'])
def menu():
    if 'username' in session:
        username = session['username']
        return render_template('menu.html', logged_in=True, username=username)
    else:
        return render_template('menu.html', logged_in=False)



@app.route("/add_to_basket", methods=['POST'])
def add_to_basket():
    if 'username' not in session:
        flash("You must be logged in to add items to your basket.", 'danger')
        return redirect(url_for('login'))

    item_name = request.form.get('item_name')
    item_price = request.form.get('item_price')
    user_id = db_session.query(Cont).filter_by(username=session['username']).first().id

    basket_item = BasketItem(user_id=user_id, item_name=item_name, item_price=item_price)
    db_session.add(basket_item)
    db_session.commit()

    flash("The item was successfully added to your basket!", 'success')

    return redirect(url_for('menu'))



@app.route("/basket", methods = ['GET', 'POST'])
def basket():
    if 'username' not in session:
        flash("You must be logged in to view your basket", 'danger')
        return redirect(url_for('login'))

    user_id = db_session.query(Cont).filter_by(username=session['username']).first().id
    basket_items = db_session.query(BasketItem).filter_by(user_id=user_id).all()

    total_price = sum(item.item_price for item in basket_items)

    return render_template('basket.html', items=basket_items, total_price=total_price)


@app.route("/remove_item/<int:item_id>", methods=['POST'])
def remove_item(item_id):
    item_to_remove = db_session.query(BasketItem).filter_by(id=item_id).first()
    if item_to_remove:
        db_session.delete(item_to_remove)
        db_session.commit()
        flash("Item has been removed from your basket!", 'success')
    else:
        flash("Item not found in basket", 'danger')

    return redirect(url_for('basket'))



@app.route("/history")
def history():
    if 'username' not in session:
        flash("You must be logged in to view your order history", 'danger')
        return redirect(url_for('login'))

    user_id = db_session.query(Cont).filter_by(username=session['username']).first().id
    orders = db_session.query(Order).filter_by(user_id=user_id).all()

    return render_template('history.html', orders=orders)


@app.route("/place_order", methods=['POST'])
def place_order():
    print(1)
    user_id = db_session.query(Cont).filter_by(username=session['username']).first().id
    address = request.form.get('address')
    phone_number = request.form.get('phone_number')
    print(address)
    print(phone_number)
    if address == None or phone_number == None:
        print(4)
        flash("Please fill in the required fields!", 'danger')
        return redirect(url_for('basket'))

    print(3)
    basket_items = db_session.query(BasketItem).filter_by(user_id=user_id).all()
    items_list = ', '.join([item.item_name for item in basket_items])

    new_order = Order(user_id=user_id, adress=address, phone_number=phone_number, items=items_list)
    db_session.add(new_order)
    db_session.query(BasketItem).filter_by(user_id=user_id).delete()
    db_session.commit()
    print(5)

    threading.Thread(target=update_order_status, args=(new_order.id,)).start()

    flash("Order placed successfully!", 'success')
    return redirect(url_for('history'))


def update_order_status(order_id):
    time.sleep(10)
    order = db_session.query(Order).filter_by(id=order_id).first()
    if order:
        order.status = "Delivered"
        db_session.commit()




if __name__ == '__main__':
    app.run(debug=True)