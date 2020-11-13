from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from flaskstagram_web.util.helpers import generate_client_token, transact, find_transaction, TRANSACTION_SUCCESS_STATUSES
from models.user import User
from models.image import Image
from models.payment import Payment
from flaskstagram_web.util.mail_helper import send_email

payments_blueprint = Blueprint('payments',
                                __name__,
                                template_folder='templates')

@payments_blueprint.route('/<image_id>/new', methods=['GET'])
@login_required
def new(image_id):
    user = User.get_or_none(User.id == current_user.id)
    image = Image.get_or_none(Image.id == image_id)
    if user:
        if image:
            client_token = generate_client_token()
            return render_template('payments/new.html', client_token=client_token, image=image)
        else: 
            flash('No image found!', 'danger')
            return redirect(url_for('images.new'))
    else:
        flash('No user found!', 'danger')
        return redirect(url_for('home'))

@payments_blueprint.route('/<image_id>', methods=['POST'])
@login_required
def create_checkout(image_id):
    user = User.get_or_none(User.id == current_user.id)
    image = Image.get_or_none(Image.id == image_id)
    if user: 
        amount = request.form['amount']
        if int(amount) >= 10:
            result = transact({
                'amount': amount,
                'payment_method_nonce': request.form['payment_method_nonce'],
                'options': {
                    "submit_for_settlement": True
                }
            })
            if result.is_success or result.transaction:
                payment = Payment(sender=user, image=image, amount=amount)
                payment.save()

                # Send thank you email to the user
                send_email(payment.sender, payment.image, amount)
               
                return redirect(url_for('payments.show_checkout', transaction_id=result.transaction.id))
            else:
                for x in result.errors.deep_errors: 
                    flash('Error: %s: %s' % (x.code, x.message), 'danger')
                return redirect(url_for('payments.new', image_id=image.id))
        else: 
            flash('Payment less than 9!', 'danger')
            return redirect(url_for('payments.new', image_id=image.id)) 
    else:
        flash("No user found!", "danger")
        return redirect(url_for('home'))


@payments_blueprint.route('/<transaction_id>', methods=['GET'])
@login_required
def show_checkout(transaction_id):
    transaction = find_transaction(transaction_id)
    result = {}
    if transaction.status in TRANSACTION_SUCCESS_STATUSES:
        flash('Sweet Success!', 'success')
        result = {
            'header': 'Payment Success!',
            'icon': 'success',
            'message': 'Your test transaction has been successfully processed. See the Braintree API response and try again.'
        }
    else:
        flash('Transaction Failed', 'danger')
        result = {
            'header': 'Transaction Failed',
            'icon': 'fail',
            'message': 'Your test transaction has a status of ' + transaction.status + '. See the Braintree API response and try again.'
        }

    return render_template('payments/show.html', transaction=transaction, result=result)