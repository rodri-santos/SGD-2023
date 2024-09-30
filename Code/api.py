import flask
import logging
import psycopg2
from dotenv import dotenv_values

app = flask.Flask(__name__)

StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500,
    'not_found': 404
}

###################
# Database Access##
###################
config = dotenv_values(".env")

def db_connection():
    try:
        db = psycopg2.connect(
            user=config.get("USER"),
            password=config.get("PASSWORD"),
            host=config.get("HOST"),
            port=config.get("PORT"),
            database=config.get("DATABASE")
        )
        return db
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

'''

--------------------- Endpoints

'''

@app.route('/')
def home():
    return "Welcome to the Pet Store API!"

#########################
# 1. Create Item (POST)##
#########################
@app.route('/proj/api/createitem', methods=['POST'])
def add_produto():
    logger.info('POST /proj/api/createitem')

    data = flask.request.get_json()
    logger.debug(f'POST /proj/api/createitem - Data: {data}')

    conn = db_connection()
    cur = conn.cursor()

    if 'produto_id' not in data:
        response = {'status': StatusCodes['api_error'], 'results': 'produto_id not in data'}
        return flask.jsonify(response)

    if 'stock' in data and data['stock'] <= 0:
        response = {'status': StatusCodes['api_error'], 'results': 'stock tem que ser maior ou igual a 0'}
        return flask.jsonify(response)

    if 'preco' in data and data['preco'] < 0:
        response = {'status': StatusCodes['api_error'], 'results': 'preco não pode ser negativo'}
        return flask.jsonify(response)

    if 'peso' in data and data['peso'] < 0:
        response = {'status': StatusCodes['api_error'], 'results': 'peso não pode ser negativo'}
        return flask.jsonify(response)

    try:
        statement = "INSERT INTO produto (produto_id, nome, stock, descricao, fabrica, peso, url_imagem, preco, categoria_categoria_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (data['produto_id'], data['nome'], data['stock'], data['descricao'], data['fabrica'], data['peso'],data['url_imagem'], data['preco'], data['categoria_categoria_id'])
        cur.execute(statement, values)
        conn.commit()

        logger.debug('POST /proj/api/createitem - Item inserted successfully')

        response = {
            'status': StatusCodes['success'],
            'message': "Item created successfully",
            'data': {
                'id': data['produto_id'],
                'name': data['nome'],
                'category': data['categoria_categoria_id'],
                'price': data['preco'],
                'stock': data['stock'],
                'description': data['descricao'],
                'manufacturer': data['fabrica'],
                'weight': data['peso'],
                'image_url': data['url_imagem']
            }
        }

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /proj/api/createitem - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'message': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

########################
# 2. Update Item (PUT)##
########################
@app.route('/proj/api/items/<int:produto_id>', methods=['PUT'])
def update_produto(produto_id):
    logger.info(f'PUT /proj/api/items/{produto_id}')

    data = flask.request.get_json()
    logger.debug(f'PUT /proj/api/items/{produto_id} - Data: {data}')

    conn = db_connection()
    cur = conn.cursor()

    #if 'produto_id' not in data:
        #response = {'status': StatusCodes['api_error'], 'results': 'produto_id not in data'}
        #return flask.jsonify(response)

    if 'stock' in data and data['stock'] <= 0:
        response = {'status': StatusCodes['api_error'], 'results': 'stock tem que ser maior ou igual a 0'}
        return flask.jsonify(response)

    if 'peso' in data and data['peso'] < 0:
        response = {'status': StatusCodes['api_error'], 'results': 'peso não pode ser negativo'}
        return flask.jsonify(response)

    if 'preco' in data and data['preco'] < 0:
        response = {'status': StatusCodes['api_error'], 'results': 'preco não pode ser negativo'}
        return flask.jsonify(response)

    try:
        statement = "UPDATE produto SET nome = %s, stock = %s, descricao = %s, fabrica = %s, peso = %s, url_imagem = %s, preco = %s, categoria_categoria_id = %s WHERE produto_id = %s"
        values = (data['nome'], data['stock'], data['descricao'], data['fabrica'], data['peso'], data['url_imagem'], data['preco'], data['categoria_categoria_id'], produto_id)
        cur.execute(statement, values)
        conn.commit()

        logger.debug(f'PUT /proj/api/items/{produto_id} - Item updated successfully')

        response = {
            'status': StatusCodes['success'],
            'message': f"Item {produto_id} updated successfully",
            'data': {
                'id': produto_id,
                'name': data['nome'],
                'category': data['categoria_categoria_id'],
                'price': data['preco'],
                'stock': data['stock'],
                'description': data['descricao'],
                'manufacturer': data['fabrica'],
                'weight': data['peso'],
                'image_url': data['url_imagem']
            }
        }

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'PUT /proj/api/items/{produto_id} - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'message': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

##############################################
# 3. Delete Item from Shopping Cart (DELETE)##
##############################################
@app.route('/proj/api/cart/<int:produto_produto_id>/<int:carrinho_cliente_cliente_id>', methods=['DELETE'])
def delete_item_carrinho(carrinho_cliente_cliente_id,produto_produto_id,):
    logger.info(f'DELETE /proj/api/cart/{carrinho_cliente_cliente_id}/{produto_produto_id}/')

    conn = db_connection()
    cur = conn.cursor()

    try:
        query = "DELETE FROM produtocarrinho WHERE produto_produto_id = %s AND carrinho_cliente_cliente_id = %s;"
        cur.execute(query, (carrinho_cliente_cliente_id, produto_produto_id, ))
        conn.commit()

        logger.debug(f'DELETE /proj/api/cart/{carrinho_cliente_cliente_id}/{produto_produto_id} - Item removed successfully')

        response = {'status': StatusCodes['success'], 'message': "Item removed from the shopping cart successfully", 'data': None}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'DELETE /proj/api/cart/{carrinho_cliente_cliente_id}/{produto_produto_id}/ - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'message': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

#######################################
# 4. Add Item to Shopping Cart (POST)##
#######################################
@app.route('/proj/api/cart/<int:carrinho_cliente_cliente_id>', methods=['POST'])
def add_item_carrinho(carrinho_cliente_cliente_id):
    logger.info(f'POST /proj/api/cart/{carrinho_cliente_cliente_id}')

    data = flask.request.get_json()
    logger.debug(f'POST /proj/api/cart/{carrinho_cliente_cliente_id} - Data: {data}')

    conn = db_connection()
    cur = conn.cursor()

    if 'item_id' not in data:
        response = {'status': StatusCodes['api_error'], 'message': 'item_id not in data'}
        return flask.jsonify(response)

    if 'quantity' in data and data['quantity'] < 0:
        response = {'status': StatusCodes['api_error'], 'results': 'quantidade tem que ser maior que 0'}
        return flask.jsonify(response)

    statement = "INSERT INTO produtocarrinho (quantidade, produto_produto_id, carrinho_cliente_cliente_id) VALUES (%s, %s, %s)"
    values = (data['quantity'], data['item_id'], carrinho_cliente_cliente_id)

    try:
        cur.execute(statement, values)
        conn.commit()

        logger.debug(f'POST /proj/api/cart/{carrinho_cliente_cliente_id} - Item added to the shopping cart successfully')

        response = {
            'status': StatusCodes['success'],
            'message': f"Item added to the shopping cart {carrinho_cliente_cliente_id} successfully",
            'data': None
        }

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /proj/api/cart/{carrinho_cliente_cliente_id} - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'message': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

###########################
# 5. Get Items List (GET)##
###########################
@app.route('/proj/api/items', methods=['GET'])
def get_produtos_list():
    logger.info('GET /proj/api/items')

    conn = db_connection()
    cur = conn.cursor()
    produtos = []

    try:
        query = "SELECT * FROM produto"
        cur.execute(query)
        rows = cur.fetchall()

        logger.debug('GET /proj/api/items - Query executed successfully')

        for row in rows:
            produto = {
                'id': row[0],
                'name': row[1],
                'category': row[8],
                'price': row[7],
                'stock': row[2],
                'description': row[3],
                'manufacturer': row[4],
                'weight': row[5],
                'image_url': row[6],
                'total_unit_sales': 0
            }
            produtos.append(produto)

        query = "SELECT produto_produto_id, SUM(quantidade) as total_unit_sales FROM produtocompra GROUP BY produto_produto_id"
        cur.execute(query)
        rows = cur.fetchall()

        logger.debug('GET /proj/api/items - Query executed successfully')
        for row in rows:
            for produto in produtos:
                if produto['id'] == row[0]:
                    produto['total_unit_sales'] = row[1]
                    break

        response = {
            'status': StatusCodes['success'],
            'message': "Items retrieved successfully",
            'data': produtos
        }

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /proj/api/items - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'message': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

#############################
# 6. Get Item Details (GET)##
#############################
@app.route('/proj/api/items/<int:produto_id>', methods=['GET'])
def get_produto(produto_id):
    logger.info(f'GET /proj/api/items/{produto_id}')

    conn = db_connection()
    cur = conn.cursor()

    try:
        statement = "SELECT * FROM produto WHERE produto_id = %s"
        values = (produto_id,)
        cur.execute(statement, values)
        row = cur.fetchone()

        if row is not None:
            produto = {
                'id': row[0],
                'name': row[1],
                'category': row[8],
                'price': row[7],
                'stock': row[2],
                'description': row[3],
                'manufacturer': row[4],
                'weight': row[5],
                'image_url': row[6]
            }

            response = {
                'status': StatusCodes['success'],
                'message': f"Item {produto_id} details retrieved successfully",
                'data': produto
            }
        else:
            response = {
                'status': StatusCodes['not_found'],
                'message': f"Item {produto_id} not found",
                'data': None
            }

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /proj/api/items - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'message': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

#########################
# 7. Search Items (GET)##
#########################
@app.route('/proj/api/items/<string:keyword>', methods=['GET'])
def search_produto_keyword(keyword):
    logger.info('GET /proj/api/items/<keyword>')
    logger.debug(f'keyword: {keyword}')

    conn = db_connection()
    cur = conn.cursor()

    try:
        query = f'''SELECT * FROM produto WHERE nome LIKE '%{keyword}%' '''
        cur.execute(query)
        rows = cur.fetchall()

        logger.debug('GET /proj/api/items/search - Query executed successfully')

        produtos = []

        for row in rows:
            produto = {
                'id': row[0],
                'name': row[1],
                'category': row[8],
                'price': row[7],
                'stock': row[2],
                'description': row[3],
                'manufacturer': row[4],
                'weight': row[5],
                'image_url': row[6]
            }
            produtos.append(produto)

        response = {
            'status': StatusCodes['success'],
            'message': "Items retrieved successfully",
            'data': produtos
        }

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /proj/api/items/search - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'results': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

#########################################
# 8. Get Top 3 Sales per Category (GET)##
#########################################
@app.route('/proj/api/stats/sales', methods=['GET'])
def get_top_sales_per_category():
    logger.info('GET proj/api/stats/sales')

    conn = db_connection()
    cur = conn.cursor()

    try:
        query = f'''WITH ranked_products AS (
                          SELECT
                            categoria.categoria_id,
                            categoria.nome AS category_name,
                            produtocompra.produto_produto_id,
                            produto.nome AS item_name,
                            SUM(produtocompra.quantidade * produtocompra.preco) AS total_value,
                            RANK() OVER (PARTITION BY categoria.categoria_id ORDER BY SUM(produtocompra.quantidade * produtocompra.preco) DESC) AS rnk
                          FROM produtocompra
                            INNER JOIN produto ON produtocompra.produto_produto_id = produto.produto_id
                            INNER JOIN categoria ON produto.categoria_categoria_id = categoria.categoria_id
                          GROUP BY categoria.categoria_id, produtocompra.produto_produto_id, item_name
                        )
                        SELECT categoria_id, category_name, produto_produto_id, item_name, total_value
                        FROM ranked_products
                        WHERE rnk <= 3
                        ORDER BY categoria_id, rnk
                       '''
        cur.execute(query)
        rows = cur.fetchall()

        logger.debug('GET proj/api/stats/sales - Query executed successfully')

        results = {}
        for row in rows:
            categoria_id = int(row[0])
            category_name = str(row[1])
            produto_produto_id = int(row[2])
            item_name = str(row[3])
            total_value = round(float(row[4]),2)

            if categoria_id not in results:
                results[categoria_id] = []

            results[categoria_id].append({"item_name": item_name, "total_value": total_value})

        formatted_results = [{"Category {}".format(key): value} for key, value in results.items()]
        response = {'status': StatusCodes['success'], 'message': "Top 3 sales per category retrieved successfully", 'data': {'top_sales_per_category': formatted_results}}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET proj/api/stats/sales - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'results': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

############################
# 9. Purchase Items (POST)##
############################
@app.route('/proj/api/purchase', methods=['POST'])
def add_purchase():
    logger.info('POST /proj/api/purchase')
    data = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /proj/api/purchase - Data: {data}')

    try:
        if "cart" not in data or "client_id" not in data:
            response = {'status': StatusCodes['api_error'], 'results': 'Invalid cart format, cart or client_id is required'}
            return flask.jsonify(response)

        for i in data["cart"]:
            if "item_id" not in i or "quantity" not in i:
                response = {'status': StatusCodes['api_error'],
                            'results': 'item_id or quantity is required to insert purchase'}
                return flask.jsonify(response)

        statement = 'SELECT COUNT(*) FROM carrinho WHERE cliente_cliente_id = %s'
        values = (data['client_id'],)
        cur.execute(statement, values)
        carrinho_exists = cur.fetchone()[0] > 0

        if carrinho_exists:
            statement = 'DELETE FROM carrinho WHERE cliente_cliente_id = %s'
            values = (data['client_id'],)
            cur.execute(statement, values)
            conn.commit()

        statement = 'INSERT INTO carrinho (data, cliente_cliente_id) VALUES (current_date, %s)'
        values = (data['client_id'],)
        cur.execute(statement, values)
        conn.commit()
        logger.debug(f'POST /proj/api/purchase - Carrinho added successfully')

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /proj/api/purchase - error(carrinho): {error}')
        conn.rollback()

    total = 0
    try:
        for item in data["cart"]:
            statement = 'SELECT stock, preco FROM produto WHERE produto_id = %s'
            values = (item["item_id"],)
            cur.execute(statement, values)
            result = cur.fetchone()

            if result:
                available_stock, price = result
                if item["quantity"] <= available_stock:
                    total_price = item["quantity"] * price
                    statement = 'INSERT INTO produtocarrinho (quantidade, produto_produto_id, carrinho_cliente_cliente_id) VALUES (%s, %s, %s)'
                    values = (item["quantity"], item["item_id"], data["client_id"])
                    cur.execute(statement, values)
                    conn.commit()

                    total += total_price

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /proj/api/purchase - error(produtocarrinho): {error}')
        conn.rollback()

    try:
        query = 'SELECT MAX(compra_id) FROM compra'
        cur.execute(query)
        max_compra_id = cur.fetchone()[0]
        new_compra_id = max_compra_id + 1 if max_compra_id else 1

        statement = 'INSERT INTO compra (compra_id, data, cliente_cliente_id) VALUES (%s, current_date, %s)'
        values = (new_compra_id, data['client_id'])
        cur.execute(statement, values)
        conn.commit()
        response = {'status': StatusCodes['success'], 'message': f"Purchase successful. Order_ID:{new_compra_id}", 'data': {'order_id': new_compra_id, 'total_price':float(total)}}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /proj/api/purchase - error(compra): {error}')
        response = {'status': StatusCodes['internal_error'], 'results': str(error)}
        conn.rollback()

    try:
        query = 'SELECT MAX(compra_id) FROM compra'
        cur.execute(query)
        max_compra_id = cur.fetchone()[0]

        for item in data["cart"]:
            statement = 'SELECT preco FROM produto WHERE produto_id = %s'
            values = (item["item_id"],)
            cur.execute(statement, values)
            result = cur.fetchone()

            statement = 'INSERT INTO produtocompra (quantidade, preco, compra_compra_id, produto_produto_id) VALUES (%s, %s, %s, %s)'
            values = (item["quantity"], result, max_compra_id, item["item_id"])
            cur.execute(statement, values)
            conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /proj/api/purchase - error(produtocompra): {error}')
        response = {'status': StatusCodes['internal_error'], 'results': str(error)}
        conn.rollback()

    try:
        for item in data["cart"]:
            statement = 'SELECT stock FROM produto WHERE produto_id = %s'
            values = (item["item_id"],)
            cur.execute(statement, values)
            available_stock = cur.fetchone()[0]

            new_stock = available_stock - item["quantity"]

            statement = 'UPDATE produto SET stock = %s WHERE produto_id = %s'
            values = (new_stock, item["item_id"])
            cur.execute(statement, values)
            conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /proj/api/purchase - error(produto): {error}')
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


if __name__ == '__main__':
    # set up logging
    logger = logging.getLogger('app_logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    host = '127.0.0.1'
    port = 5000
    app.run(host=host, debug=True, threaded=True, port=port)
    logger.info(f'API v1.0 online: http://{host}:{port}')
