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
  const tempDir = path.join('..', 'temp-deploy', storeName);
  
  try {
    // Check if theme directory exists
    if (!await fs.pathExists(themeDir)) {
      throw new Error(`Theme directory not found: ${themeDir}`);
    }
    
    // Step 1: Create temp directory with theme files
    console.log('  📦 Preparing theme files...');
    await fs.remove(tempDir);
    await fs.ensureDir(tempDir);
    
    // Copy theme files to temp
    const themeContents = await fs.readdir(themeDir);
    for (const item of themeContents) {
      await fs.copy(path.join(themeDir, item), path.join(tempDir, item));
    }
    
    // Copy shared files (if they exist)
    if (await fs.pathExists(sharedDir)) {
      const sharedContents = await fs.readdir(sharedDir);
      if (sharedContents.length > 0) {
        console.log('  🎨 Applying shared overrides...');
        for (const item of sharedContents) {
          await fs.copy(path.join(sharedDir, item), path.join(tempDir, item), { overwrite: true });
        }
      }
    }
    
    // Step 2: Ensure branch exists
    console.log(`  🌿 Checking branch ${branch}...`);
    try {
      await execPromise(`git rev-parse --verify ${branch}`);
      console.log(`    Branch ${branch} exists`);
    } catch {
      console.log(`    Creating branch ${branch}...`);
      // Create orphan branch (no history)
      await execPromise(`git checkout --orphan ${branch}`);
      // Remove all files from index
      await execPromise('git rm -rf . 2>/dev/null || true');
      // Clean working directory
      const files = await fs.readdir('.');
      for (const file of files) {
        if (file !== '.git') {
          await fs.remove(file);
        }
      }
      // Create initial commit
      await fs.writeFile('README.md', `# ${storeName} Theme\n\nThis branch contains the deployed theme for ${storeName}.`);
      await execPromise('git add README.md');
      await execPromise(`git commit -m "Initial commit for ${branch}"`);
      await execPromise('git checkout main');
    }
    
    // Step 3: Switch to branch
    console.log(`  📝 Updating ${branch} branch...`);
    await execPromise(`git checkout ${branch}`);
    
    // Step 4: Remove old files (except .git)
    const branchFiles = await fs.readdir('.');
    for (const file of branchFiles) {
      if (file !== '.git') {
        await fs.remove(file);
      }
    }
    
    // Step 5: Copy prepared files from temp
    console.log('  📂 Copying theme to branch...');
    const tempContents = await fs.readdir(tempDir);
    for (const item of tempContents) {
      await fs.copy(path.join(tempDir, item), item);
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
    
    // Clean up temp directory
    await fs.remove(tempDir);
    
    console.log(`✅ Successfully deployed ${storeName}!`);
    console.log(`   Branch ${branch} is ready.`);
    console.log(`   Run 'git push origin ${branch}' to push to GitHub.\n`);
    
  } catch (error) {
    console.error(`❌ Error deploying ${storeName}:`, error.message);
    // Try to switch back to main on error
    try {
      await execPromise('git checkout main');
    } catch {}
    // Clean up temp directory
    try {
      await fs.remove(tempDir);
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