import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import { spawn } from 'child_process'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const backendDir = path.resolve(__dirname, '..', 'backend')
const bridgeScript = path.resolve(backendDir, 'bridge.py')

/**
 * Custom Vite Plugin: Local Python Bridge
 * Intercepts `/__bridge_rpc` during development to execute the local Python process
 * directly via stdio (spawn child_process) without running any external HTTP/REST server.
 */
function pythonBridgePlugin(): Plugin {
  return {
    name: 'vite-python-bridge-plugin',
    configureServer(server) {
      server.middlewares.use('/__bridge_rpc', (req, res) => {
        if (req.method !== 'POST') {
          res.statusCode = 405
          res.end(JSON.stringify({ status: 'error', message: 'Method Not Allowed' }))
          return
        }

        let body = ''
        req.on('data', chunk => {
          body += chunk
        })

        req.on('end', () => {
          // Spawn local python process directly
          const pyProcess = spawn('python', [bridgeScript], {
            cwd: backendDir,
          })

          let stdoutData = ''
          let stderrData = ''

          pyProcess.stdout.on('data', data => {
            stdoutData += data.toString()
          })

          pyProcess.stderr.on('data', data => {
            stderrData += data.toString()
          })

          pyProcess.on('error', err => {
            res.statusCode = 500
            res.setHeader('Content-Type', 'application/json')
            res.end(
              JSON.stringify({
                status: 'error',
                message: `Failed to spawn Python process: ${err.message}`,
              })
            )
          })

          pyProcess.on('close', code => {
            res.setHeader('Content-Type', 'application/json')
            if (code !== 0 && !stdoutData) {
              res.statusCode = 500
              res.end(
                JSON.stringify({
                  status: 'error',
                  message: `Python process exited with code ${code}`,
                  stderr: stderrData,
                })
              )
              return
            }

            try {
              // Return the bridge response
              res.statusCode = 200
              res.end(stdoutData)
            } catch (err: any) {
              res.statusCode = 500
              res.end(
                JSON.stringify({
                  status: 'error',
                  message: `Invalid output from Python: ${err.message}`,
                  raw: stdoutData,
                })
              )
            }
          })

          // Send request payload to Python's stdin
          pyProcess.stdin.write(body)
          pyProcess.stdin.end()
        })
      })
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), pythonBridgePlugin()],
  server: {
    port: 5173,
    strictPort: true,
  },
})
