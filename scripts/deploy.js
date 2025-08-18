#!/usr/bin/env node
const fs = require('fs-extra');
const path = require('path');
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

// Store to branch mappings
const STORE_BRANCHES = {
  'build4less': 'build4less-live',
  'tiles4less': 'tiles4less-live',
  'building-supplies-online': 'bso-live',
  'insulation4less': 'insulation4less-live',
  'insulation4us': 'insulation4us-live',
  'roofing4us': 'roofing4us-live'
};

async function deployStore(storeName) {
  const branch = STORE_BRANCHES[storeName];
  if (!branch) {
    throw new Error(`Unknown store: ${storeName}`);
  }

  console.log(`\n🚀 Deploying ${storeName} to branch ${branch}...`);
  
  const themeDir = path.join('themes', storeName);
  const sharedDir = 'shared';
  
  try {
    // Check if theme directory exists
    if (!await fs.pathExists(themeDir)) {
      throw new Error(`Theme directory not found: ${themeDir}`);
    }
    
    // Step 1: Ensure branch exists
    console.log(`  🌿 Checking branch ${branch}...`);
    try {
      await execPromise(`git rev-parse --verify ${branch}`);
      console.log(`    Branch ${branch} exists`);
    } catch {
      console.log(`    Creating branch ${branch}...`);
      await execPromise(`git checkout -b ${branch}`);
      await execPromise('git checkout main');
    }
    
    // Step 2: Switch to branch
    console.log(`  📝 Updating ${branch} branch...`);
    await execPromise(`git checkout ${branch}`);
    
    // Step 3: Remove old files (except .git)
    const branchFiles = await fs.readdir('.');
    for (const file of branchFiles) {
      if (file !== '.git' && file !== 'node_modules') {
        await fs.remove(file);
      }
    }
    
    // Step 4: Copy theme files to root
    console.log('  📦 Copying theme files...');
    const themeContents = await fs.readdir(themeDir);
    for (const item of themeContents) {
      await fs.copy(path.join(themeDir, item), item);
    }
    
    // Step 5: Copy shared files (if they exist)
    if (await fs.pathExists(sharedDir)) {
      const sharedContents = await fs.readdir(sharedDir);
      if (sharedContents.length > 0) {
        console.log('  🎨 Applying shared overrides...');
        for (const item of sharedContents) {
          await fs.copy(path.join(sharedDir, item), item, { overwrite: true });
        }
      }
    }
    
    // Step 6: Commit changes
    console.log('  💾 Committing changes...');
    await execPromise('git add -A');
    
    try {
      const message = `Deploy ${storeName} theme - ${new Date().toISOString()}`;
      await execPromise(`git commit -m "${message}"`);
      console.log('    Changes committed');
    } catch (error) {
      if (error.message.includes('nothing to commit')) {
        console.log('    No changes to commit');
      } else {
        throw error;
      }
    }
    
    // Step 7: Switch back to main
    await execPromise('git checkout main');
    
    console.log(`✅ Successfully deployed ${storeName}!`);
    console.log(`   Branch ${branch} is ready.`);
    console.log(`   Run 'git push origin ${branch}' to push to GitHub.\n`);
    
  } catch (error) {
    console.error(`❌ Error deploying ${storeName}:`, error.message);
    // Try to switch back to main on error
    try {
      await execPromise('git checkout main');
    } catch {}
    throw error;
  }
}

// Main execution
async function main() {
  const storeName = process.argv[2];
  
  if (!storeName) {
    console.error('Usage: node scripts/deploy.js <store-name>');
    console.error('Available stores:', Object.keys(STORE_BRANCHES).join(', '));
    process.exit(1);
  }
  
  try {
    await deployStore(storeName);
  } catch (error) {
    console.error('Deployment failed:', error.message);
    process.exit(1);
  }
}

main();