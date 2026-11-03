import request from "./request";

const gateway = {
  addUser(params) {
    return request("/proctor", "post", {
      action: "index",
      image: params.image,
      fullName: params.fullName,
    });
  },

  processImage(image) {
    return request("/proctor", "post", {
      action: "process",
      image,
    });
  },
};

export default gateway;
