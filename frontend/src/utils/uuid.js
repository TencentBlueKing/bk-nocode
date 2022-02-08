export const random4 = () => Math.floor((1 + Math.random()) * 0x10000)
  .toString(16)
  .substring(1);

export const uuid = (group = 8) => {
  let id = '';
  for (let i = 0; i < group - 1; i++) {
    id += random4();
  }
  return id;
};
