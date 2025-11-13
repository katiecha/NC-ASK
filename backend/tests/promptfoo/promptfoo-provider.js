/**
 * Custom Promptfoo Provider for NC-ASK API
 * This allows better integration with the NC-ASK backend for testing
 */

class NcAskProvider {
  constructor(options) {
    this.apiUrl = options.config?.apiUrl || 'http://localhost:8000/api/query';
    this.viewType = options.config?.viewType || 'patient';
  }

  id() {
    return 'nc-ask-provider';
  }

  async callApi(prompt, context) {
    const viewType = context.vars?.view_type || this.viewType;

    try {
      const response = await fetch(this.apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: prompt,
          view_type: viewType,
          session_id: 'promptfoo-test-' + Date.now(),
        }),
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      // Return both the text response and the full object for assertions
      return {
        output: JSON.stringify(data),
        tokenUsage: {}, // We don't track tokens, but promptfoo expects this
      };
    } catch (error) {
      return {
        error: error.message,
        output: JSON.stringify({ error: error.message }),
      };
    }
  }
}

module.exports = NcAskProvider;
