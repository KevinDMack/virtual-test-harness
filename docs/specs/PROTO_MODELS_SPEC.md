# Protocol Buffers (Proto) Models Specification

## Overview

This document specifies the requirements for using Protocol Buffers (proto3) for all data models in the TTRPG Game Notes project. Proto files provide a language-neutral, platform-neutral, extensible mechanism for serializing structured data.

## Purpose

Using Protocol Buffers for data models ensures:
- **Type Safety:** Strongly-typed data structures with compile-time validation
- **Consistency:** Single source of truth for data models across all components
- **Versioning:** Built-in support for backward and forward compatibility
- **Cross-Platform:** Models work across C#, Go, JavaScript, and other languages
- **Performance:** Efficient binary serialization format
- **Documentation:** Self-documenting data structures

## Proto File Organization

### Directory Structure
All proto files must be located in the `proto/` directory at the repository root:

```
ttrpg-game-notes/
├── proto/
│   ├── campaign.proto
│   ├── note.proto
│   ├── weather_models.proto
│   └── ...
```

### File Naming Conventions
- Use **snake_case** for proto file names (e.g., `weather_models.proto`, `health_response.proto`)
- Use descriptive names that clearly indicate the model's purpose
- Keep file names concise but meaningful
- One proto file per logical data model or closely related group of models

### ❌ Do NOT Create Models Outside Proto Directory
- **NEVER** create C# model classes in `web-app/Models/` or `function-app/Models/`
- **NEVER** create duplicate data structures outside the proto directory
- All data models must originate from proto definitions

## Proto File Structure

### Required Elements

Every proto file must include:

1. **Syntax Declaration** (proto3)
```protobuf
syntax = "proto3";
```

2. **C# Namespace Option**
```protobuf
option csharp_namespace = "TtrpgTools.Models";
```

3. **Package Declaration**
```protobuf
package ttrpgtools;
```

4. **Message Definitions**
```protobuf
message ModelName {
  // Field definitions
}
```

### Complete Example

```protobuf
syntax = "proto3";

option csharp_namespace = "TtrpgTools.Models";

package ttrpgtools;

message HealthResponse {
  string status = 1;
  string database = 2;
  string timestamp = 3;
}
```

## Naming Conventions

### Message Names
- Use **PascalCase** for message names (e.g., `HealthResponse`, `WeatherEntry`, `DiceRollResult`)
- Use descriptive, noun-based names
- Avoid abbreviations unless widely understood

### Field Names
- Use **snake_case** for field names (e.g., `user_id`, `created_at`, `weather_type`)
- Use descriptive names that clearly indicate the field's purpose
- Avoid single-letter names except for well-known cases (e.g., `x`, `y` for coordinates)

### Field Numbers
- Assign unique field numbers starting from 1
- **NEVER reuse field numbers** (critical for backward compatibility)
- Reserve numbers 1-15 for frequently used fields (more efficient encoding)
- Use numbers 16+ for less common fields
- Keep numbering sequential when possible for readability

## Data Types

### Scalar Types
Use proto3 scalar types appropriately:

| Proto Type | C# Type | Use Case |
|------------|---------|----------|
| `string` | `string` | Text data, IDs |
| `int32` | `int` | Standard integers |
| `int64` | `long` | Large integers, timestamps |
| `bool` | `bool` | Boolean flags |
| `double` | `double` | Floating-point numbers |
| `float` | `float` | Single-precision floats |
| `bytes` | `ByteString` | Binary data |

### Complex Types
- **Nested Messages:** Define sub-messages for complex structures
- **Enums:** Use for fixed sets of values
- **Repeated Fields:** Use for arrays/lists (`repeated string items = 1;`)
- **Maps:** Use for key-value pairs (`map<string, int32> scores = 1;`)

### Example with Various Types
```protobuf
message Campaign {
  int32 id = 1;
  string name = 2;
  string description = 3;
  repeated Note notes = 4;
  map<string, string> metadata = 5;
  CampaignStatus status = 6;
}

enum CampaignStatus {
  CAMPAIGN_STATUS_UNSPECIFIED = 0;
  CAMPAIGN_STATUS_ACTIVE = 1;
  CAMPAIGN_STATUS_ARCHIVED = 2;
}
```

## Enum Guidelines

### Enum Naming
- Use **SCREAMING_SNAKE_CASE** for enum values
- Prefix enum values with the enum type name to avoid conflicts
- Always include a `_UNSPECIFIED` value as 0 (proto3 default)

### Enum Best Practices
```protobuf
enum WeatherType {
  WEATHER_TYPE_UNSPECIFIED = 0;  // Required default
  WEATHER_TYPE_CLEAR = 1;
  WEATHER_TYPE_CLOUDY = 2;
  WEATHER_TYPE_RAIN = 3;
  WEATHER_TYPE_SNOW = 4;
}
```

## C# Integration

### Namespace Standard
All generated C# classes must use the namespace:
```protobuf
option csharp_namespace = "TtrpgTools.Models";
```

This ensures consistency across all C# projects.

### Code Generation
Proto files are compiled to C# classes during the build process:
- Generated files are automatically created in the output directory
- **NEVER** manually edit generated C# files
- **NEVER** commit generated files to source control

### Using Generated Models in C#
```csharp
using TtrpgTools.Models;

public class WeatherService
{
    public WeatherEntry CreateWeatherEntry(string description)
    {
        return new WeatherEntry
        {
            Description = description,
            Temperature = 72,
            WeatherType = WeatherType.Clear
        };
    }
}
```

## Versioning and Compatibility

### Backward Compatibility Rules

**Always Safe:**
- Adding new fields
- Adding new enum values (except as default/first)
- Adding new messages

**Never Safe:**
- Changing field numbers
- Changing field types
- Removing fields (use deprecation instead)
- Reusing field numbers

### Field Deprecation
Instead of removing fields, mark them as deprecated:
```protobuf
message OldModel {
  int32 id = 1;
  string old_field = 2 [deprecated = true];
  string new_field = 3;
}
```

### Reserved Fields
When permanently removing fields, reserve their numbers:
```protobuf
message Campaign {
  reserved 2, 5, 9 to 11;
  reserved "old_field", "deprecated_field";
  
  int32 id = 1;
  string name = 3;
}
```

## Documentation

### Field Comments
Document all non-obvious fields:
```protobuf
message Note {
  int32 id = 1;  // Unique identifier
  string title = 2;  // Note title (max 200 characters)
  string content = 3;  // Note content in Markdown format
  int64 created_at = 4;  // Unix timestamp in seconds
}
```

### Message Comments
Document the purpose of each message:
```protobuf
// Represents a single weather entry for a specific game date
// Used by both web-app and function-app for weather generation
message WeatherEntry {
  string description = 1;
  int32 temperature = 2;
  WeatherType weather_type = 3;
}
```

## Validation Requirements

### Before Committing Proto Changes

- [ ] Proto file is in `proto/` directory
- [ ] File uses `syntax = "proto3";`
- [ ] C# namespace is set to `"TtrpgTools.Models"`
- [ ] Package is set to `ttrpgtools`
- [ ] Message names use PascalCase
- [ ] Field names use snake_case
- [ ] Field numbers are unique and never reused
- [ ] Enums include `_UNSPECIFIED` as value 0
- [ ] Complex fields are properly documented
- [ ] No duplicate models exist outside proto directory
- [ ] Proto compiles successfully
- [ ] Generated C# code builds without errors

### Build Verification
After adding or modifying proto files:
```bash
# Verify proto compilation
dotnet build web-app
dotnet build function-app

# Run tests to ensure no breaking changes
dotnet test
```

## Common Patterns

### ID Fields
```protobuf
message Entity {
  int32 id = 1;  // Use int32 for database IDs
}
```

### Timestamps
```protobuf
message Event {
  int64 created_at = 1;  // Unix timestamp in seconds
  int64 updated_at = 2;
}
```

### Lists/Collections
```protobuf
message Campaign {
  repeated Note notes = 1;
  repeated string tags = 2;
}
```

### Optional Fields
In proto3, all fields are optional by default. Use wrapper types for explicit nullability:
```protobuf
import "google/protobuf/wrappers.proto";

message User {
  google.protobuf.Int32Value age = 1;  // Explicitly nullable int
}
```

### Nested Messages
```protobuf
message Campaign {
  int32 id = 1;
  Details details = 2;
  
  message Details {
    string description = 1;
    string setting = 2;
  }
}
```

## Anti-Patterns to Avoid

❌ **Creating Models Outside Proto Directory**
```csharp
// DON'T: Create models in C# directly
namespace TtrpgTools.Models
{
    public class Campaign  // ❌ Wrong
    {
        public int Id { get; set; }
    }
}
```

✅ **Always Define in Proto**
```protobuf
// DO: Define in proto/campaign.proto
message Campaign {
  int32 id = 1;
}
```

❌ **Reusing Field Numbers**
```protobuf
message Bad {
  // int32 old_field = 1;  // Removed
  string new_field = 1;  // ❌ Reusing number 1
}
```

✅ **Reserve Removed Field Numbers**
```protobuf
message Good {
  reserved 1;  // Previously used by old_field
  string new_field = 2;  // ✅ Use new number
}
```

## Tools and Commands

### Validate Proto Syntax
Proto compilation happens automatically during build, but you can validate manually:
```bash
# Build projects to trigger proto compilation
cd web-app && dotnet build
cd function-app && dotnet build
```

### View Generated Code
Generated C# files are in:
- `web-app/obj/Debug/net10.0/` (or similar build output directory)
- Look for files named after your proto messages

## References

- [Protocol Buffers Language Guide (proto3)](https://protobuf.dev/programming-guides/proto3/)
- [Protocol Buffers C# Tutorial](https://protobuf.dev/getting-started/csharptutorial/)
- [Protocol Buffers Style Guide](https://protobuf.dev/programming-guides/style/)
- [C# Protobuf Documentation](https://github.com/protocolbuffers/protobuf/tree/main/csharp)

## Change History

- 2026-02-13: Initial specification created