const core = require('@actions/core')
const exec = require('@actions/exec')

async function main() {
    try {
        const args = core.getInput("extra-args")
        const options = cmd.push(args.replace(/\n/g, " "))

        let cmd = ["python", "./scripts/main.py", options]

        let output = ""
        await exec.exec(cmd.join(' '), null, {
          listeners: {
            stdout: function(data) {
              output += data.toString()
            },
            stderr: function(data) {
              output += data.toString()
            }
          }
        })
        core.setOutput("output", output)
    } catch (error) {
        core.setFailed(error.message)
    }
}

main()
