# 🔧 GitHub Actions Permissions Fix

## ✅ What We Fixed

1. **Added workflow permissions** in the YAML files:
   ```yaml
   permissions:
     contents: write
     pull-requests: write
     actions: read
   ```

2. **Fixed git authentication** with proper token URL:
   ```yaml
   git remote set-url origin https://x-access-token:${{ secrets.GITHUB_TOKEN }}@github.com/${{ github.repository }}.git
   ```

## 🔍 Additional Check Needed

If the error persists, check repository settings:

### Repository Settings Check

1. **Go to your GitHub repository**
2. **Click Settings tab**
3. **Go to Actions → General**
4. **Under "Workflow permissions"**, ensure:
   - ✅ **"Read and write permissions"** is selected
   - ✅ **"Allow GitHub Actions to create and approve pull requests"** is checked

### Alternative: Use Personal Access Token

If the issue persists, you can use a Personal Access Token instead:

1. **Create PAT**: GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. **Add to repository secrets** as `PAT_TOKEN`
3. **Update checkout step** in workflows:
   ```yaml
   - name: 📥 Checkout Code
     uses: actions/checkout@v4
     with:
       fetch-depth: 0
       token: ${{ secrets.PAT_TOKEN }}
   ```

## 🚀 Test the Fix

1. **Create a new PR** to dev branch
2. **Watch the Actions tab** - the promotion should now work
3. **Check if staging branch** is created automatically

## 📝 What Should Happen

After the fix:
1. ✅ PR to dev → Tests pass
2. ✅ Merge PR → Auto-promote to staging  
3. ✅ Staging tests → Auto-promote to main
4. ✅ Main push → Deploy to production

The workflow should now have proper permissions to create and push to branches! 