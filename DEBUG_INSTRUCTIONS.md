# 🔍 DEBUG INSTRUCTIONS

## I need you to check what the frontend is sending:

### **Step 1: Open Browser DevTools**
1. Press **F12** (or Cmd+Option+I on Mac)
2. Go to **Network** tab
3. Clear the network log (trash icon)

### **Step 2: Generate Timetable**
1. Click "Generate Timetable" in the wizard
2. Watch the Network tab

### **Step 3: Find the Request**
1. Look for a request to: `/api/user-driven/generate/`
2. Click on it
3. Go to **Payload** or **Request** tab

### **Step 4: Check the Data**
Look for:
```json
{
  "config_data": {
    "teachers": [...],  // ← Should have teachers here
    "subjects": [...],  // ← Should have subjects here
    ...
  },
  "target_years": ["BE"],
  "use_user_driven": true
}
```

### **Step 5: Tell me:**
1. **Are there teachers in the payload?** (Yes/No + how many)
2. **Are there subjects in the payload?** (Yes/No + how many)
3. **What does the `teachers` array look like?** (Copy 1-2 examples)
4. **What does the `subjects` array look like?** (Copy 1-2 examples)

---

## OR: Check Server Logs

After you generate, look at the Django terminal and find these lines:

```
Teachers in config: X
Subjects in config: Y
```

**Tell me what X and Y are!**

If you see:
```
⚠️ NO WIZARD DATA TO PREPARE
```

Then the frontend isn't sending the data properly!

---

## Let me know what you find! 🔍
