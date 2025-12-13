// 🔍 PASTE THIS IN BROWSER CONSOLE TO SEE WHAT'S BEING SENT
// Open browser (F12) → Console tab → Paste this code → Press Enter

console.log("=".repeat(60));
console.log("🔍 CHECKING WIZARD CONFIGURATION");
console.log("=".repeat(60));

// Try to access the config from window or React
let config = null;

// Method 1: Check if config is in window
if (window.config) {
    config = window.config;
    console.log("✅ Found config in window.config");
} 

// Method 2: Try to find React component state
else {
    console.log("⚠️  config not in window, trying to find React state...");
    
    // Find React root
    const root = document.getElementById('root');
    if (root && root._reactRootContainer) {
        console.log("Found React root, but can't easily access state");
        console.log("💡 TIP: Check the 'Final Configuration' screen - it shows the summary");
    }
}

console.log("\n" + "=".repeat(60));
console.log("📊 CONFIGURATION STATUS:");
console.log("=".repeat(60));

if (config) {
    console.log("\n✅ Teachers:", config.teachers?.length || 0);
    if (config.teachers && config.teachers.length > 0) {
        console.log("   Sample:", config.teachers[0]);
    } else {
        console.log("   ❌ NO TEACHERS LOADED!");
    }
    
    console.log("\n✅ Subjects:", config.subjects?.length || 0);
    if (config.subjects && config.subjects.length > 0) {
        console.log("   Sample:", config.subjects[0]);
    } else {
        console.log("   ❌ NO SUBJECTS LOADED!");
    }
    
    console.log("\n✅ Years:", config.yearsManaged || []);
    console.log("✅ Department:", config.department || "Not set");
    
    console.log("\n" + "=".repeat(60));
    console.log("🎯 DIAGNOSIS:");
    console.log("=".repeat(60));
    
    if (!config.teachers || config.teachers.length === 0) {
        console.log("❌ PROBLEM: No teachers loaded!");
        console.log("   FIX: Go to 'Teacher Management' screen");
        console.log("   FIX: Click 'Load Template' button");
        console.log("   FIX: Verify you see 20 teachers listed");
    }
    
    if (!config.subjects || config.subjects.length === 0) {
        console.log("❌ PROBLEM: No subjects loaded!");
        console.log("   FIX: Load template (it includes subjects)");
    }
    
    if (config.teachers && config.teachers.length > 0 && 
        config.subjects && config.subjects.length > 0) {
        console.log("✅ ALL GOOD! You have data to generate!");
        console.log("   Teachers: " + config.teachers.length);
        console.log("   Subjects: " + config.subjects.length);
        console.log("   You can proceed with generation!");
    }
} else {
    console.log("\n⚠️  Cannot access config directly");
    console.log("\n💡 ALTERNATIVE: Check the UI");
    console.log("   1. Go to 'Final Configuration' screen");
    console.log("   2. Look for 'Teachers: X' in the summary");
    console.log("   3. If X = 0, you need to load the template!");
    console.log("   4. Go back to 'Teacher Management'");
    console.log("   5. Click 'Load Template'");
}

console.log("\n" + "=".repeat(60));
console.log("🧪 WANT TO TEST BACKEND DIRECTLY?");
console.log("=".repeat(60));
console.log("\nRun this command:");
console.log(`
fetch('http://localhost:8000/api/user-driven/test/')
  .then(r => r.json())
  .then(d => {
    console.log('✅ Backend Status:', d);
    console.log('   Teachers in DB:', d.database_status.teachers);
    console.log('   Subjects in DB:', d.database_status.subjects);
  })
  .catch(e => console.error('❌ Backend Error:', e));
`);

console.log("\n" + "=".repeat(60));
console.log("📋 QUICK CHECKLIST:");
console.log("=".repeat(60));
console.log("[ ] Backend running (port 8000)");
console.log("[ ] Frontend running (port 5173)");
console.log("[ ] Clicked 'Load Template' button");
console.log("[ ] See 20 teachers listed");
console.log("[ ] Final Config shows 'Teachers: 20'");
console.log("[ ] No console errors (red text)");
console.log("\nIf ALL boxes checked → Generation will work! ✅");
console.log("=".repeat(60));
