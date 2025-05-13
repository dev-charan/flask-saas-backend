from flask import Blueprint, request, jsonify, current_app
# Make sure your models are imported correctly (e.g., from .models import ...)
# Assuming models.py is in the same directory:
from models import db, Order, OrderItem, OrderStatus 
# Remove: from .utils import token_required
import requests # For calling product_service
from decimal import Decimal

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

@orders_bp.route('', methods=['POST'])
# Removed @token_required
def create_order(): # Removed current_user_id parameter
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Request body is missing or not JSON.'}), 400
    
    # --- USER_ID NOW EXPECTED IN REQUEST BODY ---
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'message': 'Missing "user_id" in request body.'}), 400
    # --- END USER_ID CHANGE ---

    if 'items' not in data or not isinstance(data['items'], list) or not data['items']:
        return jsonify({'message': 'Invalid order data. "items" array is required.'}), 400
    
    shipping_address = data.get('shipping_address', {}) # Optional

    order_items_data = data['items']
    new_order_items = []
    total_order_amount = Decimal('0.00')

    product_service_url = current_app.config['PRODUCT_SERVICE_URL']

    try:
        for item_data in order_items_data:
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity')

            if not product_id or not isinstance(quantity, int) or quantity <= 0:
                return jsonify({'message': f'Invalid item data for product_id {product_id}.'}), 400

            try:
                response = requests.get(f"{product_service_url}/products/{product_id}")
                response.raise_for_status()
                product_info = response.json()
                product_price = Decimal(str(product_info.get('price')))
            except requests.exceptions.RequestException as e:
                current_app.logger.error(f"Error fetching product {product_id}: {e}")
                return jsonify({'message': f'Could not retrieve product details for product ID {product_id}. Service might be down or product not found.'}), 503
            except (KeyError, ValueError, TypeError):
                current_app.logger.error(f"Invalid product data received for product {product_id}")
                return jsonify({'message': f'Invalid data received from product service for product ID {product_id}.'}), 500

            price_at_purchase = product_price
            item_total = price_at_purchase * Decimal(quantity)
            total_order_amount += item_total

            order_item = OrderItem(
                product_id=product_id,
                quantity=quantity,
                price_at_purchase=price_at_purchase
            )
            new_order_items.append(order_item)

        new_order = Order(
            user_id=user_id, # Use user_id from request body
            total_amount=total_order_amount,
            status=OrderStatus.PENDING,
            shipping_address=shipping_address,
            items=new_order_items
        )

        db.session.add(new_order)
        db.session.commit()

        return jsonify(new_order.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating order: {e}")
        return jsonify({'message': 'Failed to create order.', 'error': str(e)}), 500


@orders_bp.route('', methods=['GET'])
# Removed @token_required
def get_orders(): # Removed current_user_id parameter
    try:
        # --- MODIFIED TO GET ORDERS BY user_id QUERY PARAMETER OR ALL ORDERS ---
        user_id_filter = request.args.get('user_id', type=int)
        query = Order.query

        if user_id_filter:
            query = query.filter_by(user_id=user_id_filter)
        
        orders = query.order_by(Order.created_at.desc()).all()
        # --- END MODIFICATION ---
        
        return jsonify([order.to_dict() for order in orders]), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching orders: {e}")
        return jsonify({'message': 'Failed to fetch orders.', 'error': str(e)}), 500

@orders_bp.route('/<int:order_id>', methods=['GET'])
# Removed @token_required
def get_order(order_id): # Removed current_user_id parameter
    try:
        # --- MODIFIED TO REMOVE USER_ID CHECK ---
        order = Order.query.filter_by(id=order_id).first()
        # --- END MODIFICATION ---
        
        if not order:
            return jsonify({'message': 'Order not found.'}), 404 # Message changed slightly
        return jsonify(order.to_dict()), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching order {order_id}: {e}")
        return jsonify({'message': 'Failed to fetch order.', 'error': str(e)}), 500

@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
# Removed @token_required
def update_order_status(order_id): # Removed current_user_id parameter
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Request body is missing or not JSON.'}), 400

    new_status_str = data.get('status')

    if not new_status_str:
        return jsonify({'message': 'Status is required.'}), 400

    try:
        new_status = OrderStatus(new_status_str)
    except ValueError:
        valid_statuses = [s.value for s in OrderStatus]
        return jsonify({'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400

    try:
        order = Order.query.filter_by(id=order_id).first()
        
        if not order:
            return jsonify({'message': 'Order not found.'}), 404

        order.status = new_status
        db.session.commit()
        return jsonify(order.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating order status for {order_id}: {e}")
        return jsonify({'message': 'Failed to update order status.', 'error': str(e)}), 500
