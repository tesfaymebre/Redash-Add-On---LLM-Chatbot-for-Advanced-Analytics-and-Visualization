/**
 * Skip eslint-loader during production builds on Node 17+.
 * Redash's eslint-loader@4 is incompatible with newer ESLint APIs.
 *
 * Installed to: redash/scripts/webpack/overrides.js
 * Or set: REDASH_WEBPACK_OVERRIDES=path/to/this/file
 */
function applyOverrides(webpackConfig) {
  const rules = webpackConfig.module.rules.map((rule) => {
    if (!Array.isArray(rule.use)) {
      return rule;
    }

    const use = rule.use.filter((loader) => {
      const name = typeof loader === "string" ? loader : loader.loader;
      return !name || !String(name).includes("eslint-loader");
    });

    return { ...rule, use };
  });

  return {
    ...webpackConfig,
    module: {
      ...webpackConfig.module,
      rules,
    },
  };
}

module.exports = applyOverrides;
