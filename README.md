# BCFM Case Study


# Case Study API - FastAPI Docker ve Kubernetes Projesi

Bu proje, verilen case'e göre belirli bir response dönen ve bir health endpoint'i içeren bir REST API'yi Docker container'ında çalıştırmayı ve Kubernetes üzerinde deploy etmeyi içerir.

## 1. Adım: API'nin Yazılması

- / endpoint'ine yapılan GET isteği, case'de belirtilen yanıtı döner.
- POST endpoint'i, gönderilen body içeriğini response olarak döner.
- health endpoint'i ise Kubernetes'e deploy edildikten sonra sağlık kontrolü için kullanılacak.

## 2. Adım: Dockerfile Oluşturulması

Uygulamayı Docker container'ında çalıştırmak için bir Docker imajına ihtiyaç duydum. Bunun için aşağıdaki gibi bir Dockerfile yazdım:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Dockerfile adımları şunları içeriyor:

- Base Image: Python 3.11-slim tabanlı bir imaj seçtim.
- Çalışma Dizini: /app dizinini çalışma dizini olarak ayarladım.
- Bağımlılıkların Yüklenmesi: requirements.txt dosyasında yazdığım uygulamadıki library bağımlılıklarını yüklettim.
- Kodların Kopyalanması: Uygulama kodlarını docker imajına kopyaladım.
- Portun Açılması: 8000 portunu açarak API'yi dış dünyaya erişilebilir hale getirdim.
- Uygulamanın Başlatılması: Uygulama uvicorn kullanılarak başlattım.
## 3. Adım: Docker İmajının Oluşturulması ve Pushlanması

Docker imajını oluşturmak için şu komutu kullandım:
```bash
docker build -t omeryenipazar/casestudyapi:0.2 .
```
Bu komut, Dockerfile'da belirtilen adımları izleyerek omeryenipazar/casestudyapi:0.2 adıyla bir Docker imajı oluşturur.

Daha sonra, bu imajı Docker Hub'a pushladım:
```bash
docker push omeryenipazar/casestudyapi:0.2
```
Bu adımda, Docker imajını Docker Hub'daki omeryenipazar/casestudyapi repository'sine yükledim, uygulamayı bir ortama deploy ettiğimde remote bir registry'den imajı çekebilmesini hedefledim.
## 4. Adım: Kubernetes Cluster'ında Deploy Etme
Docker Hub'daki imajı kullanarak, Docker Desktop'ın Kubernetes cluster'ında uygulamayı çalıştırdım.

#### deployment.yaml

deployment.yaml dosyası, Kubernetes cluster'ında pod'ları oluşturmak için kullanılır. Bu dosyada, Docker Hub'dan çekilen casestudyapi imajı kullanılarak uygulama çalıştırılır:
```bash
apiVersion: apps/v1
kind: Deployment
metadata:
  name: casestudyapi-deployment-healthy
  namespace: casestudy
spec:
  replicas: 1
  selector:
    matchLabels:
      app: casestudyapi-healthy
  template:
    metadata:
      labels:
        app: casestudyapi-healthy
    spec:
      containers:
      - name: casestudyapi-healthy
        image: omeryenipazar/casestudyapi:0.2
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5


```

#### service.yaml
service.yaml dosyası, Kubernetes cluster'ında uygulamayı dış dünyaya açmak için kullanılır:
```bash
apiVersion: v1
kind: Service
metadata:
  name: casestudyapi-service-healthy
  namespace: casestudy
spec:
  type: LoadBalancer
  selector:
    app: casestudyapi-healthy
  ports:
    - protocol: TCP
      port: 8000
      targetPort: 8000

```
Bu adımları takip ederek, uygulamam Kubernetes cluster'ında çalışır hale geldi ve health check için /health endpoint'i üzerinden izlenebilir duruma geldi.


health endpointinden 503 veren application için feature/unhealth branch'ini oluşturdum ve onun buildini aldım
unhealthy image build:
```bash
 docker build -t omeryenipazar/casestudyapi:0.5 .
```
docker push:
```bash
  docker push omeryenipazar/casestudyapi:0.5
```

uygulamaların swagger ui ı: 
```bash
http://localhost/docs
```

uygualamarın kubernetes'e deployment'ı
```bash
kubectl apply -f deployment-healthy/deployment.yaml
kubectl apply -f deployment-healthy/service.yaml
```
unhealthy deploymentlar:
```bash
kubectl apply -f deployment-unhealthy/deployment.yaml
kubectl apply -f deployment-unhealthy/service.yaml
```

### NGINX Kurulumu

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: casestudyapi-ingress
  namespace: casestudy
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: localhost
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: casestudyapi-service-healthy
            port:
              number: 8000
```
Ingress i deploy etmek için bu komutu kullandım:
```bash
kubectl apply -f deployment-healthy/ingress.yaml
```

curl ile localhost a istek attığmda ekran görüntüsündeki çıktı gözüktü. nginx İngress ile artık portsuz localhost ile erişebiliyorum

AWS Kubernetes deployment'ı ile maliyetlerden ötürü yapmadım. Fakat docker desktop kubernetes ile tamamlayabildim.

## Ekran Görüntüleri
### Unhealthy Pod
![Unhealty pod ekran görüntüsü](https://github.com/omeryenipazar/casestudy_bcfm/blob/master/images/deployment-unhealthy.jpg?raw=true)

### Describe Pod
![Unhealty pod Describe Çıktısı](https://github.com/omeryenipazar/casestudy_bcfm/blob/master/images/deployment-describe.jpg?raw=true)


### Curl With Ingress
![Curl Çıktısı](https://github.com/omeryenipazar/casestudy_bcfm/blob/master/images/curlingress.jpg?raw=true)



