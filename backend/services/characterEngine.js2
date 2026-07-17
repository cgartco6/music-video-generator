const presets = {
  male: { name: "Jax Blaze", movements: "dynamic dance" },
  female: { name: "Luna Vox", movements: "graceful performance" }
};

function createSingers(maleCustom, femaleCustom) {
  return {
    male: { ...presets.male, ...maleCustom },
    female: { ...presets.female, ...femaleCustom }
  };
}

module.exports = { createSingers };
