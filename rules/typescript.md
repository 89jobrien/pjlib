---
paths: ["**/*.ts", "**/*.tsx"]
---

# TypeScript Rules

## Bun-Only Environment

**CRITICAL**: Use `bun` for all TypeScript/JavaScript operations:

| Instead of | Use |
|------------|-----|
| `node` | `bun` |
| `npm install` | `bun install` |
| `npm run` | `bun run` |
| `npx` | `bunx` |
| `ts-node` | `bun` (runs .ts directly) |
| `jest` | `bun test` |
| `vitest` | `bun test` |

## Running TypeScript

```bash
# Run a TypeScript file directly (no compilation needed)
bun script.ts

# Run with watch mode
bun --watch script.ts

# Run tests
bun test
```

## Package Management

```bash
bun install              # Install dependencies
bun add <package>        # Add dependency
bun add -d <package>     # Add dev dependency
bun remove <package>     # Remove dependency
```

## Type Checking

```bash
bunx tsc --noEmit        # Type check without emitting
```

## Type Safety

**Always use strict TypeScript:**

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true
  }
}
```

**Prefer specific types:**

```typescript
// Good
type User = {
  id: number
  name: string
  email: string
}

function getUser(id: number): User | null {
  // ...
}

// Bad
function getUser(id: any): any {  // No type safety
  // ...
}
```

## Modern TypeScript

**Use modern syntax:**

```typescript
// Good - modern
const users = await fetchUsers()
const names = users.map(u => u.name)
const admin = users.find(u => u.role === 'admin')

// Bad - outdated
fetchUsers().then(function(users) {
  var names = []
  for (var i = 0; i < users.length; i++) {
    names.push(users[i].name)
  }
})
```

## Type Inference

**Let TypeScript infer when obvious:**

```typescript
// Good - inference works
const count = 42  // number
const items = ['a', 'b', 'c']  // string[]

// Bad - redundant annotations
const count: number = 42
const items: string[] = ['a', 'b', 'c']

// Good - explicit when needed
const config: Config = loadConfig()  // Type not obvious
```

## Error Handling

**Use Result types for expected failures:**

```typescript
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E }

function parseJSON(input: string): Result<unknown> {
  try {
    return { ok: true, value: JSON.parse(input) }
  } catch (error) {
    return { ok: false, error: error as Error }
  }
}

// Usage
const result = parseJSON(data)
if (result.ok) {
  console.log(result.value)
} else {
  console.error(result.error)
}
```

## Async/Await

**Always use async/await over promises:**

```typescript
// Good
async function fetchUserData(id: number): Promise<User> {
  const response = await fetch(`/api/users/${id}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch user: ${response.statusText}`)
  }
  return response.json()
}

// Bad
function fetchUserData(id: number): Promise<User> {
  return fetch(`/api/users/${id}`)
    .then(response => {
      if (!response.ok) {
        throw new Error(`Failed to fetch user: ${response.statusText}`)
      }
      return response.json()
    })
}
```

## Nullability

**Be explicit about null/undefined:**

```typescript
// Good
function findUser(id: number): User | null {
  return users.find(u => u.id === id) ?? null
}

// Check before use
const user = findUser(123)
if (user !== null) {
  console.log(user.name)  // Safe
}

// Bad
function findUser(id: number): User {
  return users.find(u => u.id === id)!  // Dangerous !
}
```

## Utility Types

**Use built-in utility types:**

```typescript
type User = {
  id: number
  name: string
  email: string
  role: 'admin' | 'user'
}

// Partial - all properties optional
type UserUpdate = Partial<User>

// Pick - subset of properties
type UserPreview = Pick<User, 'id' | 'name'>

// Omit - exclude properties
type UserWithoutId = Omit<User, 'id'>

// Readonly - immutable
type ImmutableUser = Readonly<User>
```

## Testing

```typescript
import { test, expect } from 'bun:test'

test('user validation', () => {
  const user = { id: 1, name: 'Alice', email: 'alice@example.com' }

  expect(user.id).toBe(1)
  expect(user.name).toBe('Alice')
})

test('async operations', async () => {
  const result = await fetchUserData(123)

  expect(result.name).toBeDefined()
  expect(result.email).toContain('@')
})
```

## Code Organization

```typescript
// types.ts - Type definitions
export type User = {
  id: number
  name: string
  email: string
}

// api.ts - API functions
import type { User } from './types'

export async function fetchUser(id: number): Promise<User> {
  // ...
}

// index.ts - Main entry
import { fetchUser } from './api'

const user = await fetchUser(123)
console.log(user.name)
```

## Avoid

- `any` type (use `unknown` if type truly unknown)
- `as` casts (use type guards instead)
- Non-null assertion `!` (check explicitly)
- `var` keyword (use `const` or `let`)
- `require()` (use `import`)
- Promises chains (use `async/await`)
- `==` operator (use `===`)

## React/TSX Specific

**Functional components with TypeScript:**

```typescript
type Props = {
  name: string
  age: number
  onUpdate?: (name: string) => void
}

export function UserCard({ name, age, onUpdate }: Props) {
  return (
    <div>
      <h2>{name}</h2>
      <p>Age: {age}</p>
      {onUpdate && <button onClick={() => onUpdate(name)}>Update</button>}
    </div>
  )
}
```

**Event handlers:**

```typescript
function handleClick(event: React.MouseEvent<HTMLButtonElement>) {
  event.preventDefault()
  // ...
}

function handleChange(event: React.ChangeEvent<HTMLInputElement>) {
  const value = event.target.value
  // ...
}
```
