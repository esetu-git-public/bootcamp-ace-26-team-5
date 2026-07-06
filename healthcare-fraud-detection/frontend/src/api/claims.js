import api from "./api";

export const getClaims = async () => {
  const res = await api.get("/claims");
  return res.data;
};

export const submitClaim = async (claim) => {
  const res = await api.post("/predict", claim);
  return res.data;
};