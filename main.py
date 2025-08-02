from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

def create_main_blueprint(db_manager, predictor):
    main_bp = Blueprint('main', __name__)
    
    @main_bp.route('/')
    def landing():
        """Landing page"""
        return render_template('landing.html')
    
    @main_bp.route('/dashboard')
    @login_required
    def dashboard():
        """User dashboard with recent predictions"""
        predictions = db_manager.get_user_predictions(current_user.id)
        return render_template('dashboard.html', predictions=predictions[:5])  # Show last 5
    
    @main_bp.route('/predict', methods=['GET', 'POST'])
    @login_required
    def predict():
        """Diabetes prediction page"""
        if request.method == 'POST':
            try:
                # Extract input features from form
                feature_names = predictor.get_feature_names()
                features = [float(request.form.get(feature)) for feature in feature_names]
                
                # Make prediction
                prediction, probability = predictor.predict(features)
                
                # Save prediction to database
                db_manager.save_prediction(current_user.id, features, prediction, probability)
                
                result = "High Risk" if prediction == 1 else "Low Risk"
                risk_level = "🔴" if prediction == 1 else "🟢"
                flash(f'Prediction: {result} {risk_level} (Probability: {probability:.1%})', 'success')
                
                return redirect(url_for('main.dashboard'))
            
            except Exception as e:
                flash(f'Error making prediction: {str(e)}', 'error')
        
        return render_template('predict.html')
    
    @main_bp.route('/history')
    @login_required
    def history():
        """View all prediction history"""
        predictions = db_manager.get_user_predictions(current_user.id)
        return render_template('history.html', predictions=predictions)
    
    @main_bp.route('/profile')
    @login_required
    def profile():
        """User profile page"""
        predictions = db_manager.get_user_predictions(current_user.id)
        prediction_count = len(predictions)
        last_prediction_date = predictions[0]['created_at'].split('.')[0] if predictions else None
        
        return render_template('profile.html', 
                             prediction_count=prediction_count,
                             last_prediction_date=last_prediction_date)
    
    return main_bp