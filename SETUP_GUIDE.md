# GeneTrace Setup & Testing Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install fastapi uvicorn sqlalchemy python-jose passlib python-multipart pydantic email-validator
pip install scikit-learn xgboost shap joblib pandas numpy
pip install reportlab  # For PDF generation
```

### 2. Start the Backend
```bash
cd d:\GENTRACE
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`
- API Docs: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

### 3. Access the Frontend
Open your browser and navigate to: `http://localhost:8000`

---

## 📋 Complete User Flow Test

### Step 1: Register
1. Go to `http://localhost:8000/register`
2. Fill in:
   - Full Name: `John Doe`
   - Email: `john@example.com`
   - Password: `password123`
   - Confirm: `password123`
3. Click "Create Account"
4. Should redirect to login page

### Step 2: Login
1. Go to `http://localhost:8000/login`
2. Enter:
   - Email: `john@example.com`
   - Password: `password123`
3. Click "Sign In"
4. Should redirect to dashboard

### Step 3: Enter Family History
1. Click "Enter Family History" or go to `/family`
2. Fill in Father's information:
   - Age: `65`
   - Diabetes: `Yes` → Severity: `Moderate` → Onset: `50`
   - Hypertension: `Yes`
   - Heart Disease: `Yes` → Severity: `Moderate` → Onset: `55`
   - Hair Loss: `No`
3. Fill in Mother's information:
   - Age: `62`
   - Diabetes: `Yes` → Severity: `Mild` → Onset: `55`
   - Hypertension: `Yes`
   - Heart Disease: `No`
   - Hair Loss: `No`
4. Fill in Grandparents (optional):
   - Paternal Grandfather Diabetes: `Yes`
   - Maternal Grandfather Diabetes: `Yes`
5. Click "Save & Continue →"

### Step 4: Enter Personal Information
1. Fill in Demographics:
   - Gender: `Male`
   - Age: `35`
   - Height: `175` cm
   - Weight: `75` kg
   - (BMI should auto-calculate to ~24.5)
2. Fill in Lifestyle:
   - Smoker: `No`
   - Alcohol: `No`
   - Exercise: `Moderate (1–3 hrs/week)`
   - Diet: `Good`
   - Sleep: `7` hours
   - Stress: `5`
3. Click "🎯 Run Prediction"
4. Wait for prediction to complete (should show loading spinner)

### Step 5: View Results
1. Should see:
   - Overall risk score (e.g., 35.2%)
   - Individual risk cards for 4 diseases
   - Progress bars
   - Onset age estimates
   - PWIS scores
2. Click "🔍 View SHAP Explanation" to see feature importance
3. Click "💊 View Recommendations" to see personalized advice
4. Click "📄 Download PDF Report" to generate PDF

### Step 6: Test PDF Download
1. From result page, click "📄 Download PDF Report"
2. PDF should download with filename: `GeneTrace_Report_1.pdf`
3. Open PDF and verify:
   - Patient information
   - Risk summary table
   - Onset estimates
   - SHAP analysis
   - Recommendations
   - Disclaimer

### Step 7: View History
1. Go to `/history`
2. Should see table with your prediction
3. Click "View" to see detail modal
4. Click "PDF" to download report
5. Click "Delete" to remove record
   - Confirm deletion
   - Record should disappear from table

### Step 8: Test Profile
1. Go to `/profile`
2. Should see:
   - Profile information
   - Statistics (1 prediction, 0 family members)
3. Try updating name
4. Try changing password

---

## 🧪 Specific Feature Tests

### Test PDF Generation
```bash
# After running a prediction, test the PDF endpoint directly:
curl -X GET "http://localhost:8000/history/1/report?token=YOUR_TOKEN" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o report.pdf
```

### Test Delete Functionality
```bash
# Delete a prediction record:
curl -X DELETE "http://localhost:8000/history/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test History Retrieval
```bash
# Get all predictions:
curl -X GET "http://localhost:8000/history/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🐛 Troubleshooting

### Issue: PDF Download Not Working
**Solution:**
1. Ensure `reportlab` is installed: `pip install reportlab`
2. Check browser console for errors (F12)
3. Verify token is being passed correctly in URL
4. Check backend logs for errors

### Issue: Delete Not Working
**Solution:**
1. Verify record ID is correct
2. Check that you're authenticated
3. Verify record belongs to current user
4. Check backend logs for 404 or 403 errors

### Issue: Prediction Not Running
**Solution:**
1. Ensure all models are trained and in `models/` directory
2. Check that `feature_columns.json` exists
3. Verify all required fields are filled in personal form
4. Check backend logs for validation errors

### Issue: Login Not Working
**Solution:**
1. Verify email and password are correct
2. Check that user was registered successfully
3. Clear browser cache and localStorage
4. Check backend logs for authentication errors

---

## 📊 Expected Behavior

### Risk Scores
- **Low Risk**: 0-30%
- **Moderate Risk**: 30-60%
- **High Risk**: 60-100%

### Hair Loss (Norwood Scale)
- **Stage 1-2**: Minimal risk
- **Stage 3-7**: Hereditary pattern detected

### Onset Ages
- Should be positive numbers (e.g., 45-65 years)
- N/A if not applicable

---

## 🔐 Security Notes

- Passwords are hashed with bcrypt
- JWT tokens expire after 24 hours
- All API endpoints require authentication (except public pages)
- CORS is enabled for development (restrict in production)
- Tokens are stored in localStorage (use httpOnly cookies in production)

---

## 📱 Responsive Design Test

### Mobile (375px)
- Sidebar should collapse to hamburger menu
- Tables should be scrollable
- Buttons should stack vertically
- Forms should be single column

### Tablet (768px)
- Sidebar should be visible
- 2-column layouts should work
- Tables should be readable

### Desktop (1920px)
- Full layout with sidebar
- Multi-column grids
- All features visible

---

## ✅ Final Checklist Before Deployment

- [ ] All pages load without errors
- [ ] User registration works
- [ ] User login works
- [ ] Family history form saves data
- [ ] Personal info form saves data
- [ ] Prediction runs successfully
- [ ] Results display correctly
- [ ] SHAP explanation shows
- [ ] Recommendations display
- [ ] PDF downloads successfully
- [ ] History page shows predictions
- [ ] Delete functionality works
- [ ] Profile page works
- [ ] Responsive design works on mobile
- [ ] No console errors
- [ ] No backend errors in logs

---

## 🎯 Performance Tips

1. **Lazy load models** - Models are loaded on first prediction (already implemented)
2. **Cache predictions** - Consider caching SHAP calculations
3. **Optimize PDF generation** - Consider async PDF generation for large reports
4. **Database indexing** - Add indexes on user_id and predicted_at columns

---

## 📞 Support

For issues or questions:
1. Check the backend logs: `python -m uvicorn main:app --reload`
2. Check browser console: F12 → Console tab
3. Check API docs: `http://localhost:8000/api/docs`
4. Review error messages in alert boxes

---

**Last Updated**: 2024
**Status**: ✅ All Frontend Pages Complete
