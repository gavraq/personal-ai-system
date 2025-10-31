# Step 7.6: API Integration Testing Guide

**Date**: October 27, 2025
**Status**: Ready for Testing
**Purpose**: Verify frontend Knowledge Browser displays YAML metadata from backend API

---

## Changes Made

### 1. Frontend API Client (`frontend/lib/api.ts`)
**Added 3 new knowledge API methods:**
- `getDocument(domain, category, document)` - Fetch single document with full content
- `listDocuments(domain, category)` - List documents in a category
- `getTaxonomy()` - Get complete knowledge taxonomy

**Added TypeScript Interfaces:**
```typescript
export interface KnowledgeDocument {
  domain: string
  category: string
  filename: string
  title: string
  content: string
  path: string
  cross_references: string[]
  size_bytes: number
  // YAML frontmatter fields
  slug?: string
  description?: string
  artefact_type?: string
  risk_domain?: string
  owner?: string
  approval_date?: string
  version?: string
  tags?: string[]
  related_artefacts?: Record<string, string[]>
  related_skills?: string[]
  difficulty?: string
  reading_time?: string
}

export interface KnowledgeTaxonomy {
  domains: Array<{
    name: string
    type: string
    path: string
    document_count: number
    children: Array<{...}>
  }>
  total_documents: number
  total_categories: number
  total_domains: number
}
```

### 2. Knowledge Browser Page (`frontend/app/knowledge/page.tsx`)
**Added API Integration:**
- `useEffect` hook to load documents on page mount
- API fetch using `api.getTaxonomy()` and `api.getDocument()`
- Transformation function `transformToArticle()` to map API response to UI format
- Loading and error states

**Key Features:**
- Loads all documents from taxonomy on startup
- Transforms YAML metadata to article format
- Fallback to mock data on API error
- Loading spinner during data fetch
- Error message display

**Transformation Logic:**
```typescript
function transformToArticle(doc: KnowledgeDocument): KnowledgeArticle {
  // Extract summary from description or first 200 chars
  const summary = doc.description || doc.content.substring(0, 200) + '...';

  // Parse reading time (e.g., "30 min" -> 30)
  const readTime = doc.reading_time
    ? parseInt(doc.reading_time.replace(/\D/g, ''))
    : undefined;

  return {
    id: doc.slug || doc.filename.replace('.md', ''),
    title: doc.title,
    summary: summary,
    category: doc.category,
    content: doc.content,
    tags: doc.tags || [],
    lastUpdated: doc.approval_date ? new Date(doc.approval_date) : new Date(),
    readTime: readTime,
    author: doc.owner,
    // Pass through YAML frontmatter fields
    slug: doc.slug,
    artefact_type: doc.artefact_type,
    risk_domain: doc.risk_domain,
    owner: doc.owner,
    approval_date: doc.approval_date,
    version: doc.version,
    related_artefacts: doc.related_artefacts,
    related_skills: doc.related_skills,
    difficulty: doc.difficulty,
    reading_time: doc.reading_time
  };
}
```

---

## Testing Procedure

### Step 1: Verify Backend is Running
```bash
# Check backend health
curl http://localhost:8050/health

# Expected: {"status":"healthy","service":"Risk Agents Backend",...}
```

### Step 2: Test Knowledge API Endpoints
```bash
# Test taxonomy endpoint
curl http://localhost:8050/api/knowledge/taxonomy

# Expected: JSON with domains array

# Test VAR Policy endpoint
curl http://localhost:8050/api/knowledge/market-risk/policies/var-policy.md | python3 -m json.tool | head -50

# Expected: JSON with all YAML frontmatter fields
```

### Step 3: Open Knowledge Browser in Browser
Navigate to: http://localhost:3050/knowledge

**Expected Loading Behavior:**
1. Page shows "Loading..." spinner
2. Page loads all documents from API
3. Console shows: "Loaded X knowledge documents"

### Step 4: Verify Documents Display
**Expected to see:**
- 6 total documents (2 from market-risk, 4 from change-agent)
- Categories populated in filter dropdown
- Documents displayed in grid layout

### Step 5: Test VAR Policy YAML Metadata
**Click on "Value-At-Risk Policy" document**

**Expected to see in modal:**

1. **Header Section:**
   - Title: "Value-At-Risk Policy"
   - Author: "Head of Market Risk"
   - Category: "policies"

2. **Document Metadata Section (NEW):**
   - **Badges Row:**
     - [Policy] badge (blue)
     - [Market Risk] badge (slate)
     - [Advanced] badge (red)

   - **Document Information Panel:**
     - Owner: Head of Market Risk
     - Approved: 2023-06-01
     - Version: 4.5

   - **Related Artefacts Section:**
     - methodologies: 3 items
     - models: 2 items
     - data: 2 items
     - feeds: 4 items
     - governance: 3 items
     - controls: 3 items
     - processes: 2 items
     - systems: 4 items

   - **Used by Skills Section:**
     - var-calculation
     - stress-testing
     - backtesting-analysis

3. **Content Section:**
   - Full policy text WITHOUT frontmatter (content starts with "# Value-At-Risk Policy")
   - Tags displayed (7 tags)

### Step 6: Test Stress Testing Framework
**Click on "Market Risk Stress Testing Framework" document**

**Expected to see:**
- [Framework] badge (purple instead of blue)
- [Market Risk] badge
- [Intermediate] badge (yellow instead of red)
- Owner, approval date, version
- Different related artefacts
- Different skills

### Step 7: Test Plain Markdown Documents
**Click on any "change-agent" document**

**Expected to see:**
- Standard document display (header, summary, content)
- **NO** Document Metadata section (because no YAML frontmatter)
- Backward compatibility confirmed

---

## Verification Checklist

### API Integration
- ✅ Frontend calls `/api/knowledge/taxonomy` on page load
- ✅ Frontend calls `/api/knowledge/{domain}/{category}/{document}` for each document
- ✅ API returns all YAML frontmatter fields
- ✅ No CORS errors in browser console
- ✅ No API errors in browser console

### Data Transformation
- ✅ API KnowledgeDocument transformed to KnowledgeArticle
- ✅ YAML metadata preserved in transformation
- ✅ Summary extracted from description field
- ✅ Reading time parsed to number
- ✅ Approval date converted to Date object
- ✅ Tags array handled correctly

### UI Display
- ✅ DocumentMetadata component receives article with YAML fields
- ✅ Artefact type badge displays correct color
- ✅ Risk domain badge displays
- ✅ Difficulty badge displays correct color
- ✅ Document Information panel shows owner/date/version
- ✅ Related Artefacts section displays all 8 types
- ✅ Related Skills section displays all skills
- ✅ Each skill chip is clickable/hover-able

### Backward Compatibility
- ✅ Documents without YAML frontmatter still display
- ✅ DocumentMetadata component hidden for plain Markdown
- ✅ No console errors for missing fields
- ✅ Mock data fallback works if API fails

### Error Handling
- ✅ Loading spinner displays during fetch
- ✅ Error message displays if API fails
- ✅ Individual document failures don't stop loading
- ✅ Console logs document load failures

---

## Expected Browser Console Output

```javascript
// On page load
Loaded 6 knowledge documents

// No errors
```

---

## Expected Network Activity

**Browser DevTools → Network Tab:**

1. `GET /api/knowledge/taxonomy` (200 OK)
2. `GET /api/knowledge/change-agent/meeting-management/action-items-standards.md` (200 OK)
3. `GET /api/knowledge/change-agent/meeting-management/decision-capture.md` (200 OK)
4. `GET /api/knowledge/change-agent/meeting-management/meeting-types.md` (200 OK)
5. `GET /api/knowledge/change-agent/meta/knowledge-evolution.md` (200 OK)
6. `GET /api/knowledge/market-risk/policies/stress-testing-framework.md` (200 OK)
7. `GET /api/knowledge/market-risk/policies/var-policy.md` (200 OK)

**All requests should return 200 OK with JSON response**

---

## Troubleshooting

### Issue: API Returns 404
**Symptom**: Browser console shows "Failed to load knowledge documents"
**Solution**:
- Check backend is running: `docker-compose ps`
- Restart backend: `docker-compose restart backend`
- Verify files exist: `docker-compose exec backend ls -la backend/knowledge/market-risk/policies/`

### Issue: YAML Metadata Not Displaying
**Symptom**: Documents load but metadata section missing
**Solution**:
- Open browser console
- Check if `article` object has YAML fields (e.g., `article.artefact_type`)
- Verify API response includes YAML fields: `curl http://localhost:8050/api/knowledge/market-risk/policies/var-policy.md | grep artefact_type`

### Issue: Loading Spinner Never Completes
**Symptom**: Page stuck on "Loading..." forever
**Solution**:
- Check browser console for errors
- Check Network tab for failed requests
- Verify backend health: `curl http://localhost:8050/health`

### Issue: Documents Display Wrong Category
**Symptom**: Document shows "change-agent" instead of "policies"
**Solution**:
- Check transformation function maps `doc.category` correctly
- Verify API returns correct category: `curl http://localhost:8050/api/knowledge/market-risk/policies/var-policy.md | grep category`

---

## Success Criteria

### MVP Success (Must Have)
1. ✅ Knowledge Browser loads documents from API (not mock data)
2. ✅ VAR Policy displays all YAML metadata in DocumentMetadata component
3. ✅ Stress Testing Framework displays framework-specific metadata
4. ✅ Plain Markdown documents display without errors
5. ✅ No console errors in browser

### Enhanced Success (Should Have)
6. ✅ Related artefacts chips are visually distinct and hover-able
7. ✅ Related skills chips have different styling
8. ✅ Color-coded badges match artefact types
9. ✅ Loading states provide good UX
10. ✅ Error states provide helpful messages

### Future Enhancements (Nice to Have)
11. ⏸️ Related artefacts are clickable (navigate to referenced documents)
12. ⏸️ Skills are clickable (open skill execution interface)
13. ⏸️ Filter by artefact type
14. ⏸️ Filter by risk domain
15. ⏸️ Filter by difficulty

---

## Files Modified

### Frontend
1. ✅ `frontend/lib/api.ts` - Added knowledge API methods and interfaces
2. ✅ `frontend/app/knowledge/page.tsx` - Integrated API calls and transformation

### Backend
No changes required (already complete from Step 7.4)

### Documentation
3. ✅ This test guide

---

## Next Steps After Testing

If all tests pass:
- ✅ Mark Step 7.6 complete
- ✅ Document results
- ⏸️ Proceed to Step 7.7 (Complete Module 7 documentation)

If tests fail:
- Debug specific failures using troubleshooting guide
- Fix issues in frontend code
- Re-test until all checks pass

---

## Time Estimate

- Setup verification: 2 minutes
- API endpoint testing: 3 minutes
- Browser testing: 5 minutes
- Checklist verification: 5 minutes

**Total: ~15 minutes**
