# Architecture

This document describes the architecture and organization of the monitor-watcher codebase.

## File Structure

The codebase is organized by responsibility:

```
monitor-watcher/
├── main.py              # Entry point for the application
├── monitor_switch.py    # Backwards compatibility entry point
├── cli.py               # CLI commands and Click command definitions
├── controllers.py       # Display controller implementations
├── profile_manager.py   # Profile management logic
├── constants.py         # Application constants and configuration
├── pyproject.toml       # Project dependencies and metadata
└── README.md            # User documentation
```

## Module Responsibilities

### `constants.py`
- Defines input mappings (HDMI1, DP1, etc.)
- Stores default configuration paths
- No dependencies on other modules

### `controllers.py`
- Defines the `DisplayController` abstract base class
- Implements `M1DDCController` for real hardware control via m1ddc
- Implements `MockDisplayController` for testing/dry-run mode
- Depends on: `constants.py`

### `profile_manager.py`
- Manages loading, saving, and deleting profiles from JSON
- Applies profiles to monitors via display controllers
- Handles default configuration creation
- Depends on: `constants.py`, `controllers.py`

### `cli.py`
- Defines all Click CLI commands
- Implements user interaction logic (prompts, confirmations)
- Orchestrates controllers and profile manager
- Depends on: `constants.py`, `controllers.py`, `profile_manager.py`

### `main.py`
- Application entry point
- Simply imports and runs the CLI
- Depends on: `cli.py`

### `monitor_switch.py`
- Backwards compatibility entry point
- Delegates to `main.py`
- Allows existing scripts/documentation to continue working

## Design Principles

### Single Responsibility Principle (SRP)
Each module has a single, well-defined responsibility:
- Constants: Configuration data
- Controllers: Hardware interaction
- Profile Manager: Profile persistence and application
- CLI: User interface and command routing
- Main: Application entry point

### Dependency Inversion Principle
The `DisplayController` abstract base class allows the profile manager and CLI to work with any controller implementation without knowing the details. This enables:
- Easy testing with `MockDisplayController`
- Future controller implementations (e.g., for different platforms)
- Dependency injection for better testability

### Open/Closed Principle
- New CLI commands can be added without modifying existing commands
- New controller implementations can be added without changing the interface
- New profile features can be added by extending the ProfileManager class

## Data Flow

### Applying a Profile
```
User runs command
    ↓
CLI (cli.py) parses arguments
    ↓
ProfileManager (profile_manager.py) loads profile from JSON
    ↓
ProfileManager validates and applies profile
    ↓
DisplayController (controllers.py) executes m1ddc commands
    ↓
Monitor inputs switch
```

### Creating a Profile
```
User runs create-profile
    ↓
CLI (cli.py) runs interactive wizard
    ↓
M1DDCController (controllers.py) lists available monitors
    ↓
CLI collects user input for each monitor
    ↓
ProfileManager (profile_manager.py) saves to JSON
    ↓
Configuration file updated
```

## Testing Strategy

### Dry-Run Mode
- `MockDisplayController` simulates all operations
- Tracks state changes in memory
- Provides summary of what would have been done
- Enables safe testing without hardware changes

### Future Testing
- Unit tests can mock the `DisplayController` interface
- Integration tests can use `MockDisplayController`
- End-to-end tests can run on test hardware

## Extension Points

### Adding a New Controller
1. Implement the `DisplayController` abstract class
2. Add initialization in CLI commands (like the dry-run flag)
3. No changes needed to ProfileManager or CLI logic

### Adding a New CLI Command
1. Add a new `@cli.command()` function in `cli.py`
2. Use existing ProfileManager and DisplayController instances
3. Follow Click conventions for arguments and options

### Adding Profile Features
1. Extend the JSON schema in ProfileManager
2. Add new methods to ProfileManager class
3. Update CLI commands to use new features
