# Fabric Pattern Execution

Execute a Fabric AI pattern with the provided input. Patterns are fetched from the central pattern library at fabric.gavinslater.co.uk.

## Usage

```
/fabric [pattern-name] [input]
```

## Instructions

When this command is invoked:

1. **Parse the arguments**: Extract the pattern name (first word) and the input (remaining text)

2. **Fetch the pattern**: Make a request to get the pattern content:
   ```
   GET https://fabric.gavinslater.co.uk/patterns/{pattern-name}
   Headers: X-API-Key: 971219f3d7fa7b84f8201f1cc19567e7cb687ecf0c54967a546a07533e7dbec3
   ```

3. **Execute the pattern**: Use the pattern's `content` field as the system context and process the user's input accordingly. The pattern content contains instructions for how to analyze/process the input.

4. **Return the result**: Provide the processed output in the format specified by the pattern.

## Common Patterns

- `summarize` - Create concise summary of content
- `extract_wisdom` - Extract key insights, ideas, quotes
- `extract_article_wisdom` - Extract wisdom from articles
- `analyze_claims` - Fact-check and validate claims
- `improve_writing` - Enhance text quality
- `rate_content` - Score content quality (1-10)
- `create_summary` - Generate formatted summary

## Examples

```
/fabric summarize [paste article text here]
/fabric extract_wisdom [paste transcript here]
/fabric improve_writing [paste draft text here]
```

## List Available Patterns

To see all 235+ available patterns:
```
curl -s "https://fabric.gavinslater.co.uk/patterns" -H "X-API-Key: 971219f3d7fa7b84f8201f1cc19567e7cb687ecf0c54967a546a07533e7dbec3" | jq '.patterns'
```

## Error Handling

- If pattern not found, list similar patterns
- If no input provided, prompt for input
- If API unavailable, report error clearly
