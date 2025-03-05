from flask  import Flask, render_template, redirect, request, session
from BodyFat import bodyfatdetect
import mysql.connector
import re

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="registration"
)


app = Flask(__name__)
app.secret_key = 'your_secret_key'

diet_exercise_recommendations = {
    "neck": {
        "low": {
            "diet": {
                "morning": "Omelet with spinach and avocado.",
                "afternoon": "Grilled chicken salad with olive oil.",
                "evening": "Low-fat yogurt with berries.",
                "night": "Steamed fish with green beans."
            },
            "exercise": {
                "morning": "Neck stretches (3x10), isometric resistance (3x10).",
                "evening": "Light yoga for neck flexibility (3x10)."
            }
        },
        "medium": {
            "diet": {
                "morning": "Boiled eggs with whole-grain toast.",
                "afternoon": "Skinless chicken with quinoa.",
                "evening": "Low-fat milk with nuts.",
                "night": "Grilled turkey and steamed broccoli."
            },
            "exercise": {
                "morning": "Moderate neck resistance (3x8).",
                "evening": "Side-to-side stretches (3x10)."
            }
        },
        "high": {
            "diet": {
                "morning": "Oats with almond milk and banana.",
                "afternoon": "Lentil soup with whole-grain bread.",
                "evening": "Fruit salad with low-fat yogurt.",
                "night": "Steamed veggies and grilled tofu."
            },
            "exercise": {
                "morning": "Light neck stretches (2x10).",
                "evening": "Gentle yoga for neck support (2x8)."
            }
        }
    },
    "abdomen": {
        "low": {
            "diet": {
                "morning": "Greek yogurt with granola and berries.",
                "afternoon": "Grilled chicken with quinoa and veggies.",
                "evening": "Protein shake with a handful of nuts.",
                "night": "Baked salmon with spinach and sweet potato."
            },
            "exercise": {
                "morning": "Plank holds (3x1 min), leg raises (3x12).",
                "evening": "Russian twists (3x20), mountain climbers (3x15)."
            }
        },
        "medium": {
            "diet": {
                "morning": "Oatmeal with chia seeds and banana.",
                "afternoon": "Grilled turkey breast with steamed broccoli.",
                "evening": "Low-fat cheese with cucumber slices.",
                "night": "Grilled fish with asparagus and brown rice."
            },
            "exercise": {
                "morning": "Bicycle crunches (3x15), modified planks (3x30 sec).",
                "evening": "Flutter kicks (3x12), standing side bends (3x15)."
            }
        },
        "high": {
            "diet": {
                "morning": "Vegetable smoothie with spinach, cucumber, and apple.",
                "afternoon": "Lentil soup with whole-wheat bread.",
                "evening": "Fruit salad with low-fat yogurt.",
                "night": "Steamed vegetables and grilled tofu."
            },
            "exercise": {
                "morning": "Modified planks (2x30 sec), seated twists (2x12).",
                "evening": "Gentle side bends (2x10), yoga stretches for the abdomen."
            }
        }
    },
    "waist": {
        "low": {
            "diet": {
                "morning": "Egg white omelet with spinach.",
                "afternoon": "Grilled chicken wrap with lettuce and tomatoes.",
                "evening": "Low-fat yogurt with almonds.",
                "night": "Baked chicken breast with sautéed veggies."
            },
            "exercise": {
                "morning": "Side planks (3x30 sec), waist twists (3x15).",
                "evening": "Oblique crunches (3x12), torso rotations (3x20)."
            }
        },
        "medium": {
            "diet": {
                "morning": "Smoothie with oats, banana, and almond milk.",
                "afternoon": "Steamed fish with brown rice and veggies.",
                "evening": "Low-fat cottage cheese with apple slices.",
                "night": "Grilled turkey with quinoa and green beans."
            },
            "exercise": {
                "morning": "Standing twists (3x15), moderate side planks (3x15 sec).",
                "evening": "Oblique crunches (3x10), torso rotations (3x15)."
            }
        },
        "high": {
            "diet": {
                "morning": "Vegetable juice with chia seeds and flaxseed.",
                "afternoon": "Lentil soup with whole-grain bread.",
                "evening": "Fruit salad with a handful of nuts.",
                "night": "Grilled tofu with steamed vegetables."
            },
            "exercise": {
                "morning": "Side bends (2x10), seated twists (2x12).",
                "evening": "Light yoga poses for waist flexibility (2x8)."
            }
        }
    },
    "hip": {
        "low": {
            "diet": {
                "morning": "Scrambled eggs with avocado and toast.",
                "afternoon": "Grilled salmon with quinoa and kale.",
                "evening": "Greek yogurt with berries.",
                "night": "Baked chicken with roasted Brussels sprouts."
            },
            "exercise": {
                "morning": "Glute bridges (3x15), squats (3x20).",
                "evening": "Step-ups (3x12 each leg), donkey kicks (3x15)."
            }
        },
        "medium": {
            "diet": {
                "morning": "Oatmeal with nuts and banana.",
                "afternoon": "Turkey sandwich with whole-grain bread.",
                "evening": "Low-fat milk with almonds.",
                "night": "Grilled fish with sautéed spinach."
            },
            "exercise": {
                "morning": "Bodyweight squats (3x15), wall sits (3x30 sec).",
                "evening": "Side-lying clamshells (3x12 each side)."
            }
        },
        "high": {
            "diet": {
                "morning": "Green smoothie with spinach, cucumber, and banana.",
                "afternoon": "Lentil stew with brown rice.",
                "evening": "Low-fat yogurt with fruit.",
                "night": "Steamed vegetables with grilled tofu."
            },
            "exercise": {
                "morning": "Modified glute bridges (2x10), light yoga stretches.",
                "evening": "Low-intensity side lunges (2x8)."
            }
        }
    },
    "thigh": {
        "low": {
            "diet": {
                "morning": "Egg whites with spinach and toast.",
                "afternoon": "Grilled chicken with quinoa and asparagus.",
                "evening": "Protein shake with almonds.",
                "night": "Baked salmon with sweet potato."
            },
            "exercise": {
                "morning": "Bulgarian split squats (3x10 each leg), lunges (3x12).",
                "evening": "Step-ups (3x15 each leg), leg presses (3x12)."
            }
        },
        "medium": {
            "diet": {
                "morning": "Oatmeal with blueberries and chia seeds.",
                "afternoon": "Skinless chicken with steamed broccoli.",
                "evening": "Low-fat yogurt with nuts.",
                "night": "Grilled turkey with green beans and brown rice."
            },
            "exercise": {
                "morning": "Bodyweight lunges (3x12), squats (3x15).",
                "evening": "Wall sits (3x30 sec), leg extensions (3x10)."
            }
        },
        "high": {
            "diet": {
                "morning": "Green smoothie with flaxseed and almond milk.",
                "afternoon": "Lentil soup with a side of brown rice.",
                "evening": "Low-fat yogurt with sliced apples.",
                "night": "Grilled tofu with roasted vegetables."
            },
            "exercise": {
                "morning": "Low-intensity squats (2x10), yoga stretches for thighs.",
                "evening": "Gentle step-ups (2x8 each leg)."
            }
        }
    },
    "biceps": {
        "low": {
            "diet": {
                "morning": "Protein shake with peanut butter and banana.",
                "afternoon": "Grilled chicken with quinoa and vegetables.",
                "evening": "Almonds with low-fat cheese.",
                "night": "Baked salmon with green beans."
            },
            "exercise": {
                "morning": "Bicep curls (3x12), hammer curls (3x12).",
                "evening": "Chin-ups (3x10), resistance band curls (3x12)."
            }
        },
        "medium": {
            "diet": {
                "morning": "Oatmeal with nuts and berries.",
                "afternoon": "Grilled turkey sandwich with whole-grain bread.",
                "evening": "Low-fat milk with nuts.",
                "night": "Grilled fish with sautéed vegetables."
            },
            "exercise": {
                "morning": "Light dumbbell curls (3x12), resistance band curls (3x10).",
                "evening": "Modified chin-ups (3x8)."
            }
        },
        "high": {
            "diet": {
                "morning": "Smoothie with spinach, cucumber, and apple.",
                "afternoon": "Lentil soup with a side of whole-grain bread.",
                "evening": "Fruit salad with low-fat yogurt.",
                "night": "Steamed vegetables and tofu."
            },
            "exercise": {
                "morning": "Resistance band curls (2x10), light dumbbell curls (2x8).",
                "evening": "Gentle stretches for biceps (2x8)."
            }
        }
    }
}


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/Login")
def login():
    return render_template("login.html")


@app.route("/Register")
def register():
    return render_template("register.html")


#============================== for Registration ==========================
@app.route("/Register_details", methods=['GET', 'POST'])
def register_details():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM rtable WHERE email = %s', (email,))

        # reg = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{6,10}$"
        pattern = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{6,10}$")
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
            return render_template('register.html', msg=msg)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email): 
            msg = 'Invalid email address!'
            return render_template('register.html', msg=msg)
        elif not re.match(r'[A-Za-z0-9]+', username): 
            msg = 'Username must contain only characters and numbers!'
            return render_template('register.html', msg=msg)
        elif not re.search(pattern,password): 
            msg = 'Password: one number, one lower case character, one uppercase character,one special symbol and must be between 6 to 10 characters long'
            return render_template('register.html', msg=msg)
        elif not username or not password or not email: 
            msg = 'Please fill out the form!'
            return render_template('register.html', msg=msg)
        else:
            val = (username, email, password)
            cursor.execute('INSERT INTO rtable values(0,%s,%s,%s)', val)
            mydb.commit()
            msg = 'You have successfully registered! Please proceed for login!'
            return render_template('login.html', msg=msg)

    else:
        msg = 'Please fill out the form Correctly!'
        return render_template('register.html', msg=msg)


#============================== for Login ==========================================================================================================================================
@app.route("/Login_verify", methods=['GET', 'POST'])
def login_verify():
    msg = ''
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM rtable WHERE email = %s AND password = %s', (email, password))
        account = cursor.fetchone()
        if account:
            session['username'] = request.form['email']
            msg = 'Logged in successfully !'
            return render_template('detection.html', msg=msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)



@app.route("/Detection")
def Detection():
    return render_template("Detection.html")

@app.route("/Detection_output", methods=["GET", "POST"])
def detection_output():
    if request.method == "POST":
        height = float(request.form["height"])
        weight = float(request.form["weight"])
        age = int(request.form["age"])
        gender = request.form["gender"]
        body_part = request.form["body_part"]

        user_data = {
            'Height': height,
            'Weight': weight,
            'Age': age,
            'Gender': gender,
            'BodyPart': body_part
        }

        try:
            result = bodyfatdetect.main_predict(user_data)
            print("Result:", [type(result), result, body_part])
            
            if type(result) == int or float:
                if 1 <= int(result) <= 25:
                    category = "low"
                elif 26 <= int(result) <= 60:
                    category = "medium"
                else:
                    category = "high"

                recommendations = diet_exercise_recommendations.get(body_part, {}).get(category, {})
                print("recommendations:", recommendations)
                diet_plan = recommendations.get("diet", {})
                exercise_plan = recommendations.get("exercise", {})

                return render_template("results.html",body_fat_percentage=f"{result:.2f}%", bodypart = body_part,
                                        diet_plan=diet_plan,exercise_plan=exercise_plan)
                # return render_template("detection.html", result=f"{result[0]:.2f}%", result2 = result[1])
        except Exception as e:
            return render_template("results.html", error=f"Error occurred: {str(e)}")
    return render_template("detection.html")



if __name__== "__main__":
    app.run(debug=True)