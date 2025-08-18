# Shopify Multisite Theme Management

This repository manages themes for multiple Shopify stores with a shared component system.

## Structure

- `/themes/` - Individual store themes
  - `/build4less/` - Build4Less theme
  - `/tiles4less/` - Tiles4Less theme
  - `/building-supplies-online/` - BSO theme
  - `/insulation4less/` - Insulation4Less theme
  - `/insulation4us/` - Insulation4Us theme
  - `/roofing4us/` - Roofing4Us theme

- `/shared/` - Shared components that override store-specific files

- `/scripts/` - Deployment and management scripts

## Branches

Each store has its own branch that Shopify syncs from:
- `build4less-live`
- `tiles4less-live`
- `bso-live`
- `insulation4less-live`
- `insulation4us-live`
- `roofing4us-live`

## Usage

### Deploy a single store
```bash
npm run deploy:build4less
```

### How it works

1. Store-specific files are in `/themes/[store-name]/`
2. Shared files are in `/shared/`
3. Deploy script copies store theme to branch root
4. Then copies shared files, overwriting any duplicates
5. Shopify automatically syncs from the branch

## Setup

1. Install dependencies:
```bash
npm install
```

2. Connect each Shopify store to its corresponding branch in GitHub

## Making Changes

### Store-specific change:
1. Edit files in `/themes/[store-name]/`
2. Run `npm run deploy:[store-name]`

### Shared change (all stores):
1. Edit files in `/shared/`
2. Run deploy for each store to propagate changes