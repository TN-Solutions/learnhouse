## Root Cause
Frontend is calling wrong URL paths - missing `/upload` segment in the route hierarchy.

**Correct paths:**
- `/api/v1/media/upload/prepare` ✅
- `/api/v1/media/upload/confirm` ✅

**Current frontend calls:**
- `/api/v1/media/prepare` ❌ (404 error)
- `/api/v1/media/confirm` ❌ (404 error)

## Fix Required

**File:** `apps/web/services/media/upload.ts`

1. Update `prepareUpload()` function:
   ```typescript
   // Change from:
   ${getBackendUrl()}/api/v1/media/prepare
   // To:
   ${getBackendUrl()}/api/v1/media/upload/prepare
   ```

2. Update `confirmUpload()` function:
   ```typescript
   // Change from:
   ${getBackendUrl()}/api/v1/media/confirm
   // To:
   ${getBackendUrl()}/api/v1/media/upload/confirm
   ```

## Verification
After fix, test all 3 migrated upload components:
- User avatar upload
- Course thumbnail upload
- Organization images upload