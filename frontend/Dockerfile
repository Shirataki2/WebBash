FROM node:latest as DEV

RUN npm install -g @vue/cli @vue/devtools --unsafe-perm=true

CMD [ "bash" ]

FROM node:latest as PROD

RUN npm install -g @vue/cli

CMD [ "bash" ]
