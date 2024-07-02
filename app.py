import os
from flask import Flask, request, redirect, url_for, render_template
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image
import requests,json
from tensorflow import expand_dims

app = Flask(__name__,static_url_path='/static')
model = load_model('foodie.h5')  

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    class_names=['biryani','bisibelebath','butter naan','masala puri chaat',
                'chappati','dhokla','dosa','gulab jamun','halwa','idly','wrap',
                'meduvadai','noodles','paniyaram','poori','samosa','tandoori chicken',
                'upma','vada pav','ven pongal']

    if request.method == 'POST':
        file = request.files['image']

        if file:
            testing_image_1 = Image.open(file)
            # preprocessing the recieved image
            testing_image_1 = testing_image_1.resize((224, 224))
            testing_image_1 = np.asarray(testing_image_1)/255.0
            testing_image_1_pred = model.predict(expand_dims(testing_image_1, axis=0))
            predicted_class = class_names[testing_image_1_pred.argmax()]
            
            # sending the predicted class on to screen
            query = predicted_class
            
            return render_template('predict_out.html',
                                   food_name = predicted_class,
                                   div_id="scan-lol")
    return 'No image uploaded'

# change serving size route
@app.route('/serving', methods=["POST"])
def serving():
    new_serving = request.form.get('serving_uni')
    other_data = request.form.get('dummy')
    
    #changing the string to the python dictionary
    other_data = eval(other_data.replace("\"", " in").replace("\'", "\"").replace("(", "_ ").replace(")", " _"))
    
    req_keys_cal = ['nf_calories','nf_total_fat','nf_saturated_fat',
                'nf_cholesterol','nf_sodium','nf_total_carbohydrate','nf_dietary_fiber',
                'nf_sugars','nf_protein','nf_potassium','nf_p',324,301,303
    ]
    for key,value in other_data.items():
        if key in req_keys_cal:
            other_data[key] = round((float(value) * float(new_serving))/float(other_data['serving_weight_grams']),2)
        
    for di in other_data["alt_measures"]:
        if di['serving_weight'] == float(new_serving):
            other_data['serving_weight_grams']=di['serving_weight']
            other_data['serving_unit']=di['measure']
            if di['serving_weight'] == 100 and di['qty']==100:
                other_data['serving_qty']=1
       
    return render_template('new-label.html', my_dict=other_data)


# for normal food item search
@app.route('/nutrients',methods=["POST"])
def nutrients():
    
    headers = {
        'Content-Type': 'application/json',
        'x-app-id': '3e55c2e6',
        'x-app-key': 'a58902ef048c9494a3faa8db6dd56e65'
    }
    data = {
        "query": request.form.get("food"),
        "include_subrecipe":1
    }
    response = requests.post('https://trackapi.nutritionix.com/v2/natural/nutrients',
                            headers=headers,
                            data=json.dumps(data))
    
    # returned json values form API
    values  = response.json()["foods"][0]
    # selecting only the required json values
    req_keys = ['food_name','brand_name','serving_qty','serving_unit','serving_weight_grams',
                'nf_calories','nf_total_fat','nf_saturated_fat','nf_cholesterol','nf_sodium',
                'nf_total_carbohydrate','nf_dietary_fiber','nf_sugars','nf_protein','nf_potassium',
                'nf_p','alt_measures','photo',324,301,303,'sub_recipe'
                ]
    my_dict = values
    
    # refactoring some required values from full_nutrients
    for x in my_dict["full_nutrients"]:
        if x['attr_id'] in [324,301,303]:
            my_dict[x['attr_id']] = x['value']
            
    # if values dont come from the json then make it to zero
    for lol in [324,301,303]:
        if not my_dict.get(lol):
            my_dict[lol] = float(0.0)
            
    
    # now removing all the other values 
    my_dict = {key: value for key, value  in my_dict.items() if key in req_keys}
    return render_template('new-label.html', my_dict=my_dict)


@app.route('/exercise',methods=["POST"])
def exercise():
    headers = {
        'Content-Type': 'application/json',
        'x-app-id': '3e55c2e6',
        'x-app-key': 'a58902ef048c9494a3faa8db6dd56e65'
    }
    data = {
    "query": request.form.get('exercise'),
    "height_cm":request.form.get('height_cm'),
    "weight_kg":request.form.get('weight_kg'),
    "age":request.form.get('age')
}
    response = requests.post('https://trackapi.nutritionix.com/v2/natural/exercise',
                            headers=headers,
                            data=json.dumps(data))
    # returned json values form api
    values  = response.json()["exercises"][0]
    
    return render_template("exercise.html",exercise_returned_value = values,
                            div_id="exercise-lol")

@app.route('/nutri-natural',methods=["POST"])
def nuti_natural():
    headers = {
        'Content-Type': 'application/json',
        'x-app-id': '3e55c2e6',
        'x-app-key': 'a58902ef048c9494a3faa8db6dd56e65'
    }
    data = {
        "query": request.form.get("recipie")
    }
    response = requests.post('https://trackapi.nutritionix.com/v2/natural/nutrients',
                            headers=headers,
                            data=json.dumps(data))
    # returned json values form api
    values  = response.json()["foods"]
    
    return render_template('nutri-natural.html',
                           values=values,
                           div_id="nutri-lol")
    
# return routes just for fun
@app.route('/ind')
def ind():
    return render_template('index.html')
if __name__ == '__main__':
    app.run(host="0.0.0.0")
