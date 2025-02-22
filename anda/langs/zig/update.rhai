let url = `https://ziglang.org/download/index.json`;
let json = get(url).json();
let name = json.master;
let v = name.version;
let d = name.version;
v.crop(7);
d.truncate(6);
rpm.version(v)
rpm.define("prerelease", d);
