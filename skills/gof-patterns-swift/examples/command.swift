// Command: closures capture an action and its undo, so history is an array of values.
struct Command {
    let name: String
    let execute: () -> Void
    let undo: () -> Void
}

final class Thermostat {
    private(set) var target = 20
    func set(_ value: Int) { target = value }
}

final class CommandHistory {
    private var done: [Command] = []

    func run(_ command: Command) {
        command.execute()
        done.append(command)
    }

    func undoLast() {
        guard let command = done.popLast() else { return }
        command.undo()
        print("undid \(command.name)")
    }
}

func setTarget(_ value: Int, on thermostat: Thermostat) -> Command {
    var previous = thermostat.target
    return Command(name: "set \(value)",
                   execute: { previous = thermostat.target; thermostat.set(value) },  // record at run time
                   undo: { thermostat.set(previous) })
}

let thermostat = Thermostat()
let history = CommandHistory()
history.run(setTarget(23, on: thermostat))
history.run(setTarget(18, on: thermostat))
print(thermostat.target)
history.undoLast()
print(thermostat.target)
history.undoLast()
print(thermostat.target)
